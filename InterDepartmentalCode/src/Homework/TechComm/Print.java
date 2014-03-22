package Homework.TechComm;

/*
 * The helpful print class, written by Bryce Summers.
 * Purpose: Provides useful functions for making it easier to print things.
 */

public class Print
{
	public static void print(Object o)
	{
		System.out.println(o);
	}
	
	public static void printArray(int[] O)
	{
		System.out.print("[");
		for(Object o: O)
		{
			System.out.print(o);
			System.out.print(", ");
		}
		System.out.print("]");
		System.out.println();
	}
	
	public static void printIntegerArray(Integer[] O)
	{
		System.out.print("[");
		for(Object o: O)
		{
			System.out.print(o);
			System.out.print(", ");
		}
		System.out.print("]");
		System.out.println();
	}
	
	public void print(int[] O)
	{
		System.out.print("[");
		for(Object o: O)
		{
			System.out.print(o);
			System.out.print(", ");
		}
		System.out.print("]");
		System.out.println();
	}
	
}
