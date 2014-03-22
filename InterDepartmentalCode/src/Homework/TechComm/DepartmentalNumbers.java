package Homework.TechComm;

/*
 * Departmental data proccessing class.
 * 
 * Written by Bryce Summers on 3 - 22 - 2014.
 * 
 * Purpose : This class assigns a bijective mapping of departments at CMU to indices. 
 */

public class DepartmentalNumbers
{

	// Takes 
	public static int getIndex(int number)
	{
		if(number < 0 || number >= 100)
		{
			throw new Error("Departments only have two digit numbers");
		}
		
		switch(number)
		{
			case 2: return 0;
			case 3: return 1;
			case 4: return 2;
			case 5: return 3;
			case 6: return 4;
			case 8: return 5;
			case 9: return 6;
			case 10: return 7;
			case 11: return 8;
			case 12: return 9;
			case 14: return 10;
			case 15: return 11;
			case 16: return 12;
			case 17: return 13;
			case 18: return 14;
			case 19: return 15;
			case 21: return 16;
			case 24: return 17;
			case 27: return 18;
			case 30: return 19;
			case 31: return 20;
			case 32: return 21;
			case 33: return 22;
			case 36: return 23;
			case 38: return 24;
			case 39: return 25;
			case 42: return 26;
			case 45: return 27;
			case 46: return 28;
			case 47: return 29;
			case 48: return 30;
			case 51: return 31;
			case 52: return 32;
			case 53: return 33;
			case 54: return 34;
			case 57: return 35;
			case 60: return 36;
			case 62: return 37;
			case 65: return 38;
			case 66: return 39;
			case 67: return 40;
			case 69: return 41;
			case 70: return 42;
			case 73: return 43;
			case 76: return 44;
			case 79: return 45;
			case 80: return 46;
			case 82: return 47;
			case 85: return 48;
			case 86: return 49;
			case 88: return 50;
			case 90: return 51;
			case 91: return 52;
			case 92: return 53;
			case 93: return 54;
			case 94: return 55;
			case 95: return 56;
			case 96: return 57;
			case 98: return 58;
			case 99: return 59;
			case 64: return 60;
			case 74: return 61;
			case 20: return 62;
		}
		
		throw new Error("The Requested Department : " + number +" is not currently supported.");
	}
	
}
