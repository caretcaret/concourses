package Homework.TechComm;

import java.io.File;


/*
 * ArrayUtil class.
 * 
 * Provides useful Array native functions for processing them.
 */

public class ArrayUtil
{
	public static void reverse(Object[] arr)
	{
		int len = arr.length;
		for(int i = 0; i < len / 2; i++)
		{
			Object temp    = arr[i];
			arr[i] = arr[len - i - 1];
			arr[len - i - 1] = temp;
		}
	}
}
