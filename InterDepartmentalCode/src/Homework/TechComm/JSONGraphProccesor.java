package Homework.TechComm;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;

import com.sun.org.apache.xerces.internal.impl.xpath.regex.ParseException;

import External_Libraries.JSON.JSONArray;
import External_Libraries.JSON.JSONObject;
import External_Libraries.JSON.parser.JSONParser;

import static Homework.TechComm.Print.*;

/*
 * This Class is the start of my efforts to effectively process a JSON file.
 * 
 * Tech Comm Group project 3 - 20 - 2014 at CMU.
 * 
 * Algorithm 1 : Transform 
 */

public class JSONGraphProccesor
{
	
	// The Beginning...
	public static void main(String[] args)
	{
		new JSONGraphProccesor();
	}
	
	// Constructor.
	public JSONGraphProccesor()
	{
		
		File dir = FileIO.parseFile("course", "F06");
		
		// Compute the directories for each semester we want to process.
		proccessCourses(dir);

	}
	
	/*
	 * REQUIRES : A list of semesters in reverse chronological order.
	 * 			  Data closer to the beginning of the array of files will 
	 * 			  overrule data from semesters later in the array.
	 * 
	 * ENSURES : Outputs a JSON file representing the computed statistics regarding
	 * 			 departments and interdepartmental corequisites.
	 */
	public void proccessCourses(File ... semesters)
	{
		// Keep track of all the courses we have seen already.
		HashSet<Integer> course_checked_set = new HashSet<Integer>();
		
		// Used to store all of the counting information for all of the departments.
		DepartmentCounter counter = new DepartmentCounter();
		
		int num_departments = 59;
		int[][] reqrs = new int[num_departments][num_departments];
		
		for(File s : semesters)
		{
			File[] courses = s.listFiles();
			
			for(File file : courses)
			{
				
				HashMap<String, Object> course = FileIO.parseJSON(file);
		
				// Avoid malformed data from files.
				if(course == null)
				{
					continue;
				}
	
				// -- Departmental counting.
				String str 			  = (String)course.get("number");
				int course_number 	  = new Integer(str);
				int department_number = getDepartment(str);
				
				// Do not process courses more than once.
				if(course_checked_set.contains(course_number))
				{
					continue;
				}
				
				// Count this course.
				counter.addCourseDepartment(department_number);
				
				
				// -- Interdepartmental coreqr / prereqr counting.

				// Corequisites
				JSONArray msg		  = (JSONArray) course.get("corequisites");
				Iterator<Object> iter = msg.iterator();
				countReqrs(reqrs, iter, department_number);
			
				// Prerequisites.
				msg	 = (JSONArray) course.get("prerequisites");
				iter = msg.iterator();
				countReqrs(reqrs, iter, department_number);
			}
		}
		
		//counter.printResults();
		saveResults(counter, reqrs);
		
	}

	// -- Private Data Types.

	// This keeps track of the number of course in each department.
	private class DepartmentCounter
	{
		// Private Data.
		LinkedHashMap<Integer, DepartmentEntry> departments = new LinkedHashMap<Integer, DepartmentEntry>();
		
		// Methods.
		
		// Increments the count of courses in the given department.
		public void addCourseDepartment(int department_number)
		{
			DepartmentEntry d = departments.get(department_number);
			
			if(d == null)
			{
				d = new DepartmentEntry(department_number);
				departments.put(department_number, d);
			}
			
			d.addCourse();			
		}
		
		public void printResults()
		{
			for(DepartmentEntry d : departments.values())
			{
				print(d);
			}
		}
		
		public JSONArray toJSONArray()
		{
			JSONArray arr = new JSONArray();
			
			for(DepartmentEntry d : departments.values())
			{
				JSONObject o = d.toJSONObject();
				arr.add(o);
			}
			
			return arr;
		}
		
	}
	

	
	// Keeps track of data specific to individual departments.
	private class DepartmentEntry
	{
		// Name of department
		String name = "Bogus";
		
		// Number of courses in this department.
		int count = 0;
		
		final int myDepartmentPrefix;
		
		public DepartmentEntry(int department_number)
		{
			myDepartmentPrefix = department_number;
		}
		
		public void addCourse()
		{
			count++;
		}
		
		public String toString()
		{
			// index++;
			// return "case " + myDepartmentPrefix + ": return " + index + ";";
			return "department = " + myDepartmentPrefix + ", count = " + count;
		}
		
		@SuppressWarnings("unchecked")
		public JSONObject toJSONObject()
		{
			JSONObject o = new JSONObject();
			o.put("number", myDepartmentPrefix);
			o.put("name", name);
			o.put("count", count);
			return o;
		}
	}

	// -- Private methods.

	// Recursively count all co and pre requisites within a coure's reqr logic.
	private void countReqrs(int[][] reqrs, Iterator<Object> iter, int department_number)
	{
		while(iter.hasNext())
		{
			Object o = iter.next();
			
			if(o instanceof JSONArray)
			{
				JSONArray jarr = (JSONArray)o;
				Iterator<Object> iter2 = jarr.iterator();
				countReqrs(reqrs, iter2, department_number);
				continue;
			}
			else if(!(o instanceof String))
			{
				throw new Error("Oh dear!");
			}
			
			String reqr_str = (String)o; 
			if(reqr_str.equals("or") || reqr_str.equals("and"))
			{
				continue;
			}
			
			// The index of the root department.
			int i = DepartmentalNumbers.getIndex(department_number);
			
			int requisite_department_number = getDepartment(reqr_str);
			
			// The index of the requisite department.
			int j = DepartmentalNumbers.getIndex(requisite_department_number);
			
			reqrs[i][j]++;
		}
	}
	
	// Save the Computed Data to a JSON file.	
	private void saveResults(DepartmentCounter counter, int[][] reqrs)
	{
		JSONObject data = new JSONObject();
		
		data.put("departments", counter.toJSONArray());
		data.put("matrix", MatrixToJSON(reqrs));
		
		File file = FileIO.parseFile("OutputData.json");
		
		FileIO.openFile(file);
		PrintStream out = FileIO.getStream(file);
		out.print(data.toJSONString());
		FileIO.closeFile(file);
	}
	
	// Creates a JSON array from the given matrice.
	@SuppressWarnings("unchecked")
	private JSONArray MatrixToJSON(int[][] arr)
	{
		JSONArray output = new JSONArray();
		
		int len = arr.length;
		
		for(int row = 0; row < len; row++)
		{
			output.add(RowToJSON(arr, row));
		}
		
		return output;
	}
	
	// Creates a JSON array from the given row.
	@SuppressWarnings("unchecked")
	private JSONArray RowToJSON(int [][] arr, int row)
	{
		JSONArray output = new JSONArray();
		
		int len = arr.length;
		for(int c = 0; c < len; c++)
		{
			output.add(arr[row][c]);
		}
		
		return output;
	}
	
	// -- Helper functions.
	private int getDepartment(int number)
	{
		return getDepartment("" + number);
	}
	
	private int getDepartment(String str)
	{
		return new Integer(str.substring(0, 2));
	}
	
}
