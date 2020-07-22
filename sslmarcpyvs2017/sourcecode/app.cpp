/*
-------------------------------------------------------------------------------------------------------------
**
** Location weighted landscape index calculation program.
**
** This class was developed to do the calculation of landscape index.
** The inputs include :
** 1. land use map(should be reclassifed to include intended sink
** and source classes).
** 2. dem : defines the elevation
** 3. slope : calculated from the DEM
** 4. distance : calculated with the path distance tool with
** dem as surface factor in ArcGIS.
**
** Qingyu Feng
** qingyufeng@outlook.com
** Department of Agricultural & Biological Engineering
** Purdue University
** West Lafayette, Indiana
**
** Jan 2018
**
**
-------------------------------------------------------------------------------------------------------------
*/


// ------------------------------------------------------------------------------------------------------------
// Including standard and customized header files:
#include <stdio.h>
#include <cstdlib>
#include <string.h>
#include <vector>
#include <iostream>
#include <sstream>
#include <cfloat>
#include <algorithm>


using namespace std;

#include "app.h"
#include "message.h"


void fatalError(const char *msg)
{
	char longMsg[1024];

	sprintf_s(longMsg, 1024, "The TOPAZ to WEPP translator program has encountered an error\nand can not continue. The error is:\n\n%s", msg);

	fprintf(stdout, "%s %s\n", longMsg, "Error calculating LWLI");
	_exit(-1);

}


/*
** App()
** Constructor for the main App object that drives everything.
*/
App::App()
{
	rows = cols = 0;
	ascelev = NULL;
	ascslope = NULL;
	ascdist = NULL;
	asclu = NULL;
	srclunums = NULL;
	sinklunums = NULL;
	allsrcsinklus = NULL;
	rawludata = NULL;
	perludata = NULL;
	lwlis = NULL;

}


/*
** ~App()
**
** Destrcutor for the main application object. Main task is to free the memory.
*/

App::~App()
{
	if (ascelev) delete ascelev;
	if (ascslope) delete ascslope;
	if (ascdist) delete (ascdist);
	if (asclu) delete (asclu);
	if (srclunums) delete (srclunums);
	if (sinklunums) delete (sinklunums);
	if (allsrcsinklus) delete (allsrcsinklus);
	if (rawludata) delete (rawludata);
	if (perludata) delete (perludata);
	if (lwlis) delete (lwlis);

}


/*
** cleanMemory()
**
** Free all the dynamically allocated memory that was used.
**
*/
void App::cleanMemory()
{
	if (ascelev) delete ascelev;
	if (ascslope) delete ascslope;
	if (ascdist) delete (ascdist);
	if (asclu) delete (asclu);
	if (srclunums) delete (srclunums);
	if (sinklunums) delete (sinklunums);
	if (allsrcsinklus) delete (allsrcsinklus);
	if (rawludata) delete (rawludata);
	if (perludata) delete (perludata);
	if (lwlis) delete (lwlis);

	ascelev = NULL;
	ascslope = NULL;
	ascdist = NULL;
	asclu = NULL;
	srclunums = NULL;
	sinklunums = NULL;
	allsrcsinklus = NULL;
	rawludata = NULL;
	perludata = NULL;
	lwlis = NULL;

}


int *App::readTextInttoArray(const char * file)
{
	FILE *fp = fopen(file, "r");
	char buf[512];
	int *data;

	if (fp)
	{
		// Define the variable after the file is opened successfully.
		data = new int[MAX_LUIDS];
		if (data == NULL)
		{
			fatalError("Out of memory in readTextInttoArray()");
		}
		memset(data, 0, sizeof(int)*MAX_LUIDS);
		int val;
		int k = 0;

		while (fgets(buf, 256, fp) != NULL)
		{
			sscanf(buf, "%d", &val);
			data[k] = val;
			++k;

		}
		fclose(fp);
	}
	else {
		perror("Error opening file");
	}

	return data;
}


/*
** combinesrcsinklus()
**
** combines sink and source array into one array.
**
*/
int *App::combineSrcSinklus()
{
	// Declaring variables
	int *data;

	// Start reading datalines
	// initiate the container data	
	data = new int[MAX_LUIDS];
	if (data == NULL)
	{
		fatalError("Out of memory in readArcviewInt()");
	}

	memset(data, 0, sizeof(int)*MAX_LUIDS);

	// Start geting the data and put them into the data
	int index = 0;

	for (int i = 0; i < MAX_LUIDS; i++)
	{
		if (srclunums[i] == 0)
		{
			break;
		}
		else
		{
			data[index] = srclunums[i];
			index++;
		}
	}

	for (int j = 0; j < MAX_LUIDS; j++)
	{
		if (sinklunums[j] == 0)
		{
			break;
		}
		else
		{
			data[index] = sinklunums[j];
			index++;
		}
	}
	return data;
}





/*
** readArcviewInt()
**
** Reads an arcview grid file and stores it into an integer array.
**
*/
int *App::readArcviewInt(const char *file)
{
	// Declaring variables
	FILE *fp = fopen(file, "r");
	char buf2[512];
	char *buf;
	char ebuf[256];
	int i;
	int *data;

	// Initiate variables
	buf = NULL;
	rows = cols = 0;

	sprintf(buf2, "Reading grid: %s ...\n", file);
	DisplayMessage(buf2);

	if (fp)
	{
		// reading the first 6 lines
		for (i = 0; i < 6; i++)
		{
			fgets(buf2, 256, fp);
			if (!strncmp(buf2, "nrows", 5))
			{
				// sscanf: read data from s and stores
				// them according to parameter formats
				// into the locations given by the additional
				// arguments: here &rows.
				sscanf(&buf2[6], "%d", &rows);
			}
			else if (!strncmp(buf2, "ncols", 5))
			{
				sscanf(&buf2[6], "%d", &cols);
			}
			else if (!strncmp(buf2, "cellsize", 8))
			{
				sscanf(&buf2[9], "%f", &cellsize);
			}
			else if (!strncmp(buf2, "NODATA_value", 6))
			{
				sscanf(&buf2[13], "%d", &noDataLu);
			}
		}

		// Start reading datalines
		// initiate the container data	
		data = new int[rows*cols];
		if (data == NULL)
		{
			fatalError("Out of memory in readArcviewInt()");
		}
		buf = new char[MAX_COL_BYTES + 1];
		if (buf == NULL)
		{
			fatalError("Out of memory in readArcviewInt()");
		}
		// memset(void *ptr, int value, std::size_t num);
		// sets the first num bytes of the block of memory pointed
		// by prt to the specified value
		// sizeof (int): return size in bytes of the object representation of type;
		// sizeof expression: return size in bytes of the object
		// representation of the type that would be returned by
		// expression. 
		//memset(data, 0, sizeof(int)*rows*cols);
		// data is a one dimension array. The total number of elements
		// is rows*cols
		memset(data, 0, sizeof(int)*rows*cols);

		// Start geting the data and put them into the data
		int k;
		int index = 0;
		int val;
		bool rowHasData;

		for (i = 0; i<rows; i++)
		{
			// i is the row number, each row has cols number of columns.
			index = i*cols;
			if (fgets(buf, MAX_COL_BYTES, fp) != NULL)
			{
				if ((i == 0) && (strlen(buf) >= MAX_COL_BYTES))
				{
					delete(buf);
					fatalError("Line too long from grid file, max is 50000 bytes");
				}

				// At this time, all validRows value is still all 1s.
				if (validRows[i])
				{
					rowHasData = false;
					k = 0;
					while (buf[k] == ' ') { k++; }
					// Start working with columns.
					// Here later, the columns might be masked by the 
					// subnoinfield.
					for (int j = 0; j < cols; j++)
					{
						sscanf(&buf[k], "%d", &val);
						// Originally, the program uses the value of bounds
						// from the outputs of Topaz. Here, we do not have a bounds
						// output from TauDEM, but we have an array of subarea numbers
						// to help determine whether the row is valid row.
						for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
						{
							// The value of subarea no will be three situations:
							// 1. no data value
							// 2. subarea no in the no data value
							// 3. subarea no not in the data value
							// If it is in field, assign, Else, other values are all 0s.
							// Data is a pointer of int. Originally, it is all 0s. 
							// now , if we have data, value is assigned to here.
							// subarea no in subnoifld, if yes, assign the values.
							if (allsrcsinklus[luidx] == 0)
							{
								break;
							}
							else if (allsrcsinklus[luidx] == val)
							{
								data[index] = val;
								rowHasData = true;
							}
						}
						//printf("Reading int..%d..%d..%d..%d..\n", i, j, index, data[index]);
						while ((buf[k] != ' ') && (buf[k] != '\n')) { k++; }
						while (buf[k] == ' ') { k++; }
						index++;
					}
					if (rowHasData == false)
					{
						validRows[i] = 0;
					}
				}
			}
		}
		delete(buf);
		fclose(fp);
	}
	else
	{
		sprintf(ebuf, "Can't find %s\n", file);
		fatalError(ebuf);
	}

	sprintf(buf2, "Done Reading Grid: %s...\n", file);
	DisplayMessage(buf2);

	return data;

}



/*
** readArcviewFloat()
**
** Reads and ArcView grid file of float values and stores them into a floating
** point array.
**
*/
float *App::readArcviewFloat(const char *file)
{
	// Declaring variables
	FILE *fp = fopen(file, "r");
	char buf2[512];
	char *buf;
	char ebuf[256];
	int i;
	float *data;

	// Initiate variables
	buf = NULL;
	rows = cols = 0;
	//int noData;

	sprintf(buf2, "Reading grid: %s ...\n", file);
	DisplayMessage(buf2);

	if (fp)
	{
		// reading the first 6 lines
		for (i = 0; i < 6; i++)
		{
			fgets(buf2, 256, fp);
			if (!strncmp(buf2, "nrows", 5))
			{
				// sscanf: read data from s and stores
				// them according to parameter formats
				// into the locations given by the additional
				// arguments: here &rows.
				sscanf(&buf2[6], "%d", &rows);
			}
			else if (!strncmp(buf2, "ncols", 5))
			{
				sscanf(&buf2[6], "%d", &cols);
			}
			else if (!strncmp(buf2, "cellsize", 8))
			{
				sscanf(&buf2[9], "%f", &cellsize);
			}
			else if (!strncmp(buf2, "NODATA_value", 6))
			{
				sscanf(&buf2[13], "%d", &noData);
			}
		}

		// Start reading datalines
		// initiate the container data	
		data = new float[rows*cols];
		if (data == NULL)
		{
			fatalError("Out of memory in readArcviewFloat()");
		}
		buf = new char[MAX_COL_BYTES + 1];
		if (buf == NULL)
		{
			fatalError("Out of memory in readArcviewFloat()");
		}
		// memset(void *ptr, int value, std::size_t num);
		// sets the first num bytes of the block of memory pointed
		// by prt to the specified value
		// sizeof (int): return size in bytes of the object representation of type;
		// sizeof expression: return size in bytes of the object
		// representation of the type that would be returned by
		// expression. 
		//memset(data, 0, sizeof(int)*rows*cols);
		// data is a one dimension array. The total number of elements
		// is rows*cols
		memset(data, 0, sizeof(float)*rows*cols);
		// Start geting the data and put them into the data
		int k;
		int index = 0;
		float val;

		for (i = 0; i<rows; i++)
		{
			// i is the row number, each row has cols number of columns.
			index = i*cols;
			if (fgets(buf, MAX_COL_BYTES, fp) != NULL)
			{
				if ((i == 0) && (strlen(buf) >= MAX_COL_BYTES))
				{
					delete(buf);
					fatalError("Line too long from grid file, max is 50000 bytes");
				}
				// At this time, all validRows value is still all 1s.
				if (validRows[i])
				{
					k = 0;
					while (buf[k] == ' ') { k++; }
					// Start working with columns.
					// Here later, the columns might be masked by the 
					// subnoinfield.
					for (int j = 0; j<cols; j++)
					{

						sscanf(&buf[k], "%f", &val);
						// Originally, the program uses the value of bounds
						// from the outputs of Topaz. Here, we do not have a bounds
						// output from TauDEM. For the last program, we got the 
						// array of subwta. If subwta not in the list, 
						// the value is assigned to 0. We will do the 
						// same thing here. 
						if (asclu[index] != 0)
						{
							data[index] = val;
						}
						// Skipping the spaces
						while ((buf[k] != ' ') && (buf[k] != '\n')) { k++; }
						while (buf[k] == ' ') { k++; }
						index++;
					}
				}
			}
		}

		delete(buf);
		fclose(fp);
	}
	else
	{
		sprintf(ebuf, "Can't find %s\n", file);
		fatalError(ebuf);
	}

	sprintf(buf2, "Done Reading Grid: %s...\n", file);
	DisplayMessage(buf2);

	return data;

}

/*
** asc2ludata()
**
** This function put the data read from the ASC files into
** the corresponding array of land use data.
**
*/
App::Ludata *App::asc2ludata()
{
	char buf2[512];
	sprintf(buf2, "Putting ascii data into corresponding land use data arrays!!\n");
	DisplayMessage(buf2);

	//Ludataarray psinksrc;
	Ludata *templudata = new Ludata;
	
	for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
	{
		// Initialize the array
		if (allsrcsinklus[luidx] == 0) { break; }
		else
		{
			templudata->elevarray[luidx] = new double[rows*cols];
			memset(templudata->elevarray[luidx], 0.0, sizeof(double)*rows*cols);
			templudata->slopearray[luidx] = new double[rows*cols];
			memset(templudata->slopearray[luidx], 0.0, sizeof(double)*rows*cols);
			templudata->distarray[luidx] = new double[rows*cols];
			memset(templudata->distarray[luidx], 0.0, sizeof(double)*rows*cols);
		}

		// Initialize the counter
		templudata->ludtctrarray[luidx] = 0;
		templudata->finaldistctr[luidx] = 0;
		templudata->finalelevctr[luidx] = 0;
		templudata->finalslpctr[luidx] = 0;

		// Initialize the luno
		templudata->luno = allsrcsinklus[luidx];
	}


	for (int index = 0; index<rows*cols; index++)
	{
		for (int luidx=0; luidx<MAX_LUIDS;luidx++)
		{ 
			if (allsrcsinklus[luidx] == 0) { break; }
			else if (asclu[index] == allsrcsinklus[luidx])
			{
				templudata->elevarray[luidx][templudata->ludtctrarray[luidx]] = ascelev[index];
				templudata->slopearray[luidx][templudata->ludtctrarray[luidx]] = ascslope[index];
				templudata->distarray[luidx][templudata->ludtctrarray[luidx]] = ascdist[index];
				templudata->ludtctrarray[luidx]++;
			}
			templudata->finaldistctr[luidx] = templudata->ludtctrarray[luidx];
			templudata->finalelevctr[luidx] = templudata->ludtctrarray[luidx];
			templudata->finalslpctr[luidx] = templudata->ludtctrarray[luidx];
		}
	}

	sprintf(buf2, "Finished putting ascii data into corresponding land use data arrays!!\n");
	DisplayMessage(buf2);


	return templudata;
}



/*
** sortludata()
**
** This function sort the ludatas.
**
*/
void App::sortludata()
{
	char buf2[512];
	sprintf(buf2, "Sorting distance, elevation and slope data!!\n");
	DisplayMessage(buf2);

	for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
	{
		if (allsrcsinklus[luidx] != 0)
		{

			// In the same loop, do the sorting:
			// Sort method is working;
			sort(rawludata->elevarray[luidx], 
				rawludata->elevarray[luidx]+rawludata->ludtctrarray[luidx]);
			sort(rawludata->slopearray[luidx],
				rawludata->slopearray[luidx] + rawludata->ludtctrarray[luidx]);
			sort(rawludata->distarray[luidx],
				rawludata->distarray[luidx] + rawludata->ludtctrarray[luidx]);


		}
		else { break; }
	}

	sprintf(buf2, "Finished sorting distance, elevation and slope data!!\n");
	DisplayMessage(buf2);


}


/*
** calperludata()
**
** This function calculate the percent of the ludatas.
**
*/
App::Ludata *App::calperludata()
{
	char buf2[512];
	sprintf(buf2, "Calculating percentage of distance, elevation and slope data!!\n");
	DisplayMessage(buf2);


	//Ludataarray psinksrc;
	Ludata *templudata = new Ludata;

	for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
	{
		// Initialize the array
		if (allsrcsinklus[luidx] == 0) { break; }
		else
		{
			// To reduce the memory use, here, we will use the total number
			// of values
			templudata->elevarray[luidx] = new double[rawludata->ludtctrarray[luidx]];
			memset(templudata->elevarray[luidx], 0.0, sizeof(double)*rawludata->ludtctrarray[luidx]);
			templudata->slopearray[luidx] = new double[rawludata->ludtctrarray[luidx]];
			memset(templudata->slopearray[luidx], 0.0, sizeof(double)*rawludata->ludtctrarray[luidx]);
			templudata->distarray[luidx] = new double[rawludata->ludtctrarray[luidx]];
			memset(templudata->distarray[luidx], 0.0, sizeof(double)*rawludata->ludtctrarray[luidx]);
		}

		// Initialize the counter
		templudata->ludtctrarray[luidx] = rawludata->ludtctrarray[luidx];
		templudata->finaldistctr[luidx] = rawludata->ludtctrarray[luidx];
		templudata->finalelevctr[luidx] = rawludata->ludtctrarray[luidx];
		templudata->finalslpctr[luidx] = rawludata->ludtctrarray[luidx];

		// Initialize the luno
		templudata->luno = allsrcsinklus[luidx];
	}

	
	for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
	{
		if (allsrcsinklus[luidx] != 0)
		{
			for (int index = 0; index < rawludata->ludtctrarray[luidx]; index++)
			{
				templudata->slopearray[luidx][index] = (double)index * (double)100. / (double)rawludata->ludtctrarray[luidx];
				templudata->distarray[luidx][index] = (double)index * (double)100. / (double)rawludata->ludtctrarray[luidx];
				templudata->elevarray[luidx][index] = (double)index * (double)100. / (double)rawludata->ludtctrarray[luidx];
			}
		}
		else { break; }
	}

	sprintf(buf2, "Finished calculating percentage of distance, elevation and slope data!!\n");
	DisplayMessage(buf2);

	return templudata;
}



/*
** removeDuplicates()
**
** This function remove duplicates in the array.
** Two arrays are taking here, dataarray stands for the ordar array.
** dataarray2 is for the percent, since the corresponding
** percentage value of the data need to be removed when the 
** value was removed.
**
*/
void App::removeDuplicates()
{

	char buf2[512];
	sprintf(buf2, "Removing duplicates in distance, elevation and slope data!!\n");
	DisplayMessage(buf2);

	for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
	{
		if (allsrcsinklus[luidx] != 0)
		{
			for (int idx = 0; idx < rawludata->ludtctrarray[luidx]-1; idx++)
				// Here, we use the final counter from the perludata.
				// This has been updated during the removal of duplicates.
			{
				if(rawludata->elevarray[luidx][idx] == rawludata->elevarray[luidx][idx+1])
				{
					rawludata->elevarray[luidx][idx] = 9999999999999999;
					perludata->elevarray[luidx][idx] = 9999999999999999;
					perludata->finalelevctr[luidx]--;
				}

				if (rawludata->distarray[luidx][idx] == rawludata->distarray[luidx][idx + 1])
				{
					rawludata->distarray[luidx][idx] = 9999999999999999;
					perludata->distarray[luidx][idx] = 9999999999999999;
					perludata->finaldistctr[luidx]--;
				}

				if (rawludata->slopearray[luidx][idx] == rawludata->slopearray[luidx][idx + 1])
				{
					rawludata->slopearray[luidx][idx] = 9999999999999999;
					perludata->slopearray[luidx][idx] = 9999999999999999;
					perludata->finalslpctr[luidx]--;
				}

			}
			sort(rawludata->elevarray[luidx],
				rawludata->elevarray[luidx] + rawludata->ludtctrarray[luidx]);
			sort(rawludata->slopearray[luidx],
				rawludata->slopearray[luidx] + rawludata->ludtctrarray[luidx]);
			sort(rawludata->distarray[luidx],
				rawludata->distarray[luidx] + rawludata->ludtctrarray[luidx]);

			sort(perludata->elevarray[luidx],
				perludata->elevarray[luidx] + perludata->ludtctrarray[luidx]);
			sort(perludata->slopearray[luidx],
				perludata->slopearray[luidx] + perludata->ludtctrarray[luidx]);
			sort(perludata->distarray[luidx],
				perludata->distarray[luidx] + perludata->ludtctrarray[luidx]);



		}
		else { break; }
	}

	sprintf(buf2, "Finished removing duplicates in distance, elevation and slope data!!\n");
	DisplayMessage(buf2);

}



/*
** caltrapzarea()
**
** Calculates the area of a trapozoid shape.
** Four inputs are required. In this application:
** 1. the x axis value (elevation, distance or slope), 
**    will be used as height of the shape.
** 2. the y axis value (percentage calculated)
**    will be used as the top (x) and bottom (x+1).
*/
double App::caltrapzarea(double olu1, double olu2, double perlu1, double perlu2)
{
	double traparea = (olu2 - olu1)*(perlu1 + perlu2) / (double)2;
	return traparea;
}




/*
** callwli()
**
** This function calculates the lorenz curve data, incluging the 
** data points and the area under each curve.
**
*/
App::Ludata *App::callwli()
{

	char buf2[512];
	sprintf(buf2, "Calculating curve areas for distance, elevation and slope data!!\n");
	DisplayMessage(buf2);
	
	//Ludataarray;
	// Here, the elevation array will only have one value for one 
	// land use, which will be the lwli value. It will be accumulated
	// during the loop.
	Ludata *templudata = new Ludata;

	

	for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
	{
		// Initialize the array
		if (allsrcsinklus[luidx] == 0) { break; }
		else
		{
			templudata->elevarray[luidx] = new double;
			memset(templudata->elevarray[luidx], 0.0, sizeof(double) * 1);
			templudata->slopearray[luidx] = new double;
			memset(templudata->slopearray[luidx], 0.0, sizeof(double) * 1);
			templudata->distarray[luidx] = new double;
			memset(templudata->distarray[luidx], 0.0, sizeof(double) * 1);
		}

		// Initialize the counter
		templudata->ludtctrarray[luidx] = 1;
		templudata->finaldistctr[luidx] = templudata->ludtctrarray[luidx];
		templudata->finalelevctr[luidx] = templudata->ludtctrarray[luidx];
		templudata->finalslpctr[luidx] = templudata->ludtctrarray[luidx];

		// Initialize the luno
		templudata->luno = allsrcsinklus[luidx];
	}


	for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
	{
		if (allsrcsinklus[luidx] != 0)
		{

			// Here, we use the final counter from the perludata.
			// This has been updated during the removal of duplicates.
			for (int index = 0; index < perludata->finalelevctr[luidx]-1; index++)
			{
				// Here, we are looping through each value in the array 
				// (elevation, distance, slope) for each land use.
				// We need a function to calculate the area for each step.
				// check the final value numbers
				templudata->elevarray[luidx][0] = templudata->elevarray[luidx][0]+ caltrapzarea(
									rawludata->elevarray[luidx][index],
									rawludata->elevarray[luidx][index + 1],
									perludata->elevarray[luidx][index],
									perludata->elevarray[luidx][index + 1]);
			}

			for (int index = 0; index < perludata->finaldistctr[luidx] - 1; index++)
			{
				// Here, we are looping through each value in the array 
				// (elevation, distance, slope) for each land use.
				// We need a function to calculate the area for each step.
				// check the final value numbers
				templudata->distarray[luidx][0] += caltrapzarea(
					rawludata->distarray[luidx][index],
					rawludata->distarray[luidx][index + 1],
					perludata->distarray[luidx][index],
					perludata->distarray[luidx][index + 1]);
			}

			for (int index = 0; index < perludata->finalslpctr[luidx] - 1; index++)
			{
				// Here, we are looping through each value in the array 
				// (elevation, distance, slope) for each land use.
				// We need a function to calculate the area for each step.
				// check the final value numbers
				templudata->slopearray[luidx][0] += caltrapzarea(
					rawludata->slopearray[luidx][index],
					rawludata->slopearray[luidx][index + 1],
					perludata->slopearray[luidx][index],
					perludata->slopearray[luidx][index + 1]);

			
			}

		}
		else { break; }
	}

	sprintf(buf2, "Finished calculating curve areas for distance, elevation and slope data!!\n");
	DisplayMessage(buf2);

	return templudata;
}


/*
** writeElevData()
**
** Write output files.
**
*/
void App::writeElevData(const char *file)
{
	char buf2[512];
	sprintf(buf2, "Writing output data for elevation!!\n");
	DisplayMessage(buf2);

	FILE *fp = fopen(file, "w");
	
	if (fp)
	{
		fprintf(fp, "No duplicated data for %s\n", file);
		for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
		{
			if (allsrcsinklus[luidx] != 0)
			{
				// Here, we use the final counter from the perludata.
				// This has been updated during the removal of duplicates.
				fprintf(fp, "Value for land use NO: %d\n", allsrcsinklus[luidx]);
				for (int index = 0; index < perludata->finalelevctr[luidx] - 2; index++)
				{
					fprintf(fp, "%f,", rawludata->elevarray[luidx][index]);
				}
				fprintf(fp, "%f\n", rawludata->elevarray[luidx][perludata->finalelevctr[luidx]-1]);

				// Here, we use the final counter from the perludata.
				// This has been updated during the removal of duplicates.
				fprintf(fp, "Percentage for land use NO: %d\n", allsrcsinklus[luidx]);
				for (int index = 0; index < perludata->finalelevctr[luidx] - 2; index++)
				{
					fprintf(fp, "%f,", perludata->elevarray[luidx][index]);
				}
				fprintf(fp, "%f\n", perludata->elevarray[luidx][perludata->finalelevctr[luidx]-1]);
			}
			else { break; }
		}
	}
	
	fclose(fp);

	sprintf(buf2, "Finished writing output data for elevation!!\n");
	DisplayMessage(buf2);

}

/*
** writeDistData()
**
** Write output files.
**
*/
void App::writeDistData(const char *file)
{
	char buf2[512];
	sprintf(buf2, "Writing output data for Distance!!\n");
	DisplayMessage(buf2);

	FILE *fp = fopen(file, "w");

	if (fp)
	{
		fprintf(fp, "No duplicated data for %s\n", file);
		for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
		{
			if (allsrcsinklus[luidx] != 0)
			{
				// Here, we use the final counter from the perludata.
				// This has been updated during the removal of duplicates.
				fprintf(fp, "Value for land use NO: %d\n", allsrcsinklus[luidx]);
				for (int index = 0; index < perludata->finaldistctr[luidx] - 2; index++)
				{
					fprintf(fp, "%f,", rawludata->distarray[luidx][index]);
				}
				fprintf(fp, "%f\n", rawludata->distarray[luidx][perludata->finaldistctr[luidx] - 2]);

				// Here, we use the final counter from the perludata.
				// This has been updated during the removal of duplicates.
				fprintf(fp, "Percentage for land use NO: %d\n", allsrcsinklus[luidx]);
				for (int index = 0; index < perludata->finaldistctr[luidx] - 2; index++)
				{
					fprintf(fp, "%f,", perludata->distarray[luidx][index]);
				}
				fprintf(fp, "%f\n", perludata->distarray[luidx][perludata->finaldistctr[luidx] - 2]);
			}
			else { break; }
		}
	}

	fclose(fp);

	sprintf(buf2, "Finished writing output data for Distance!!\n");
	DisplayMessage(buf2);
}


/*
** writeSlpData()
**
** Write output files.
**
*/
void App::writeSlpData(const char *file)
{
	char buf2[512];
	sprintf(buf2, "Writing output data for Slope!!\n");
	DisplayMessage(buf2);


	FILE *fp = fopen(file, "w");

	if (fp)
	{
		fprintf(fp, "No duplicated data for %s\n", file);
		for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
		{
			if (allsrcsinklus[luidx] != 0)
			{
				// Here, we use the final counter from the perludata.
				// This has been updated during the removal of duplicates.
				fprintf(fp, "Value for land use NO: %d\n", allsrcsinklus[luidx]);
				for (int index = 0; index < perludata->finalslpctr[luidx] - 2; index++)
				{
					fprintf(fp, "%f,", rawludata->slopearray[luidx][index]);
				}
				fprintf(fp, "%f\n", rawludata->slopearray[luidx][perludata->finalslpctr[luidx] - 2]);

				// Here, we use the final counter from the perludata.
				// This has been updated during the removal of duplicates.
				fprintf(fp, "Percentage for land use NO: %d\n", allsrcsinklus[luidx]);
				for (int index = 0; index < perludata->finalslpctr[luidx] - 2; index++)
				{
					fprintf(fp, "%f,", perludata->slopearray[luidx][index]);
				}
				fprintf(fp, "%f\n", perludata->slopearray[luidx][perludata->finalslpctr[luidx] - 2]);
			}
			else { break; }
		}
	}

	fclose(fp);

	sprintf(buf2, "Finished writing output data for Slope!!\n");
	DisplayMessage(buf2);

}


/*
** writeLwliData()
**
** Write Lwli files.
**
*/
void App::writeLwliData(const char *file)
{
	char buf2[512];
	sprintf(buf2, "Writing output data for Lorenz curve!!\n");
	DisplayMessage(buf2);

	FILE *fp = fopen(file, "w");

	if (fp)
	{
		fprintf(fp, "Area under lorenz curve\n");
		fprintf(fp, "Landuse, Area_Elevation, Area_Distance, Area_Slope\n");
		for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
		{
			if (allsrcsinklus[luidx] != 0)
			{
				// Here, we use the final counter from the perludata.
				// This has been updated during the removal of duplicates.
				fprintf(fp, "Landuse_%d, ", allsrcsinklus[luidx]);
				fprintf(fp, "%f, %f, %f\n", 
							lwlis->elevarray[luidx][0],
							lwlis->distarray[luidx][0],
							lwlis->slopearray[luidx][0]);

			}
			else { break; }
		}
	}

	fclose(fp);

	sprintf(buf2, "Finished writing output data for Lorenz curve!!\n");
	DisplayMessage(buf2);
}



/*
** writeOutputs()
**
** Write output files.
**
*/
void App::writeOutputs()
{
	// Write elevation outputs
	writeElevData("elev_dataperc.txt");
	writeDistData("dist_dataperc.txt");
	writeSlpData("slp_dataperc.txt");

	writeLwliData("LurenzCurveAreas.txt");

}




/*
** calAreaPercOverws()
**
** This function calculates the area of each land use
** over the watershed area. This will be achieved by
** count the total number of cells in the watershed
** and those in each of the sink and source landuse.
**
*/

void App::calAreaPercOverws()
{
	
	// input for this function will be
	// sinklunums
	// srclunums
	// asclu
	// Three counters will be needed:
	int *sinkluctr;
	int *srcluctr;
	int totalluctr;

	totalluctr = 0;

	// Initiate the counter values
	sinkluctr = new int[MAX_LUIDS];
	if (sinkluctr == NULL)
	{
		fatalError("Out of memory in calAreaPercOverws()");
	}
	memset(sinkluctr, 0, sizeof(int)*MAX_LUIDS);

	srcluctr = new int[MAX_LUIDS];
	if (srcluctr == NULL)
	{
		fatalError("Out of memory in calAreaPercOverws()");
	}
	memset(srcluctr, 0, sizeof(int)*MAX_LUIDS);

	for (int index = 0; index<rows*cols; index++)
	{
		
		if (asclu[index] != 0)
		{
			//printf("Reading int%d..\n", asclu[index]);
			totalluctr = totalluctr + 1;
		}

		for (int i = 0; i < MAX_LUIDS; i++)
		{
			if (srclunums[i] == 0)
			{
				break;
			}
			else if (asclu[index] == srclunums[i])
			{
				srcluctr[i] = srcluctr[i] +1;
			}
		}

		for (int j = 0; j < MAX_LUIDS; j++)
		{
			if (sinklunums[j] == 0)
			{
				break;
			}
			else if (asclu[index] == sinklunums[j])
			{
				sinkluctr[j] = sinkluctr[j] + 1;
			}
		}
	}



	// Then these will be written into a file
	char buf2[512];
	sprintf(buf2, "Writing percentage of area for each land use over watershed area!\n");
	DisplayMessage(buf2);

	FILE *fp = fopen("luareaperc.txt", "w");

	if (fp)
	{
		fprintf(fp, "Percentage of area for each land use over watershed area\n");
		fprintf(fp, "Landuse, Total_cells, Percentage\n");

		for (int luidx = 0; luidx < MAX_LUIDS; luidx++)
		{
			if (sinklunums[luidx] == 0)
			{
				break;
			}
			else
			{
				fprintf(fp, "Sink_%d, %d, %f\n", 
					sinklunums[luidx],
					sinkluctr[luidx],
					(double)sinkluctr[luidx]/(double)totalluctr);
			}
		}

		for (int luidx2 = 0; luidx2 < MAX_LUIDS; luidx2++)
		{
			if (srclunums[luidx2] == 0)
			{
				break;
			}
			else
			{
				fprintf(fp, "Source_%d, %d, %f\n",
					srclunums[luidx2],
					srcluctr[luidx2],
					(double)srcluctr[luidx2] / (double)totalluctr);
			}
		}
	}

	fclose(fp);

	sprintf(buf2, "Finished writing percentage of area for each land use over watershed area!\n");
	DisplayMessage(buf2);
}





/*
** readGisAsciiFiles()
**
** Reads in the grid files that are required. 
**
*/
void App::readGisAsciiFiles()
{
	for (int i = 0; i<MAX_ROWS; i++)
	{
		validRows[i] = 1;
	}

	// Get the land use numbers for sink and source
	srclunums = readTextInttoArray("srclus.txt");
	sinklunums = readTextInttoArray("sinklus.txt");

	allsrcsinklus = combineSrcSinklus();

	// Read in the ascii files
	asclu = readArcviewInt("luws.txt");
	ascelev = readArcviewFloat("demws.txt");
	ascslope = readArcviewFloat("slopews.txt");
	ascdist = readArcviewFloat("distws.txt");

	// put the value into corresponding lu
	rawludata = asc2ludata();
}


/*
** SortCalpercent()
**
** Sort rawdata and calculate the percent of the datas.
**
*/
void App::SortCalpercent()
{

	// Sort the data, will be stored in the orderludata
	sortludata();

	// Percent will be put into the perludata
	perludata = calperludata();

	// Remove duplicates 
	removeDuplicates();
}



void App::CalLWLI()
{
	// After processing the data, the next step is to 
	// calculate the Trapezoidal area of the data.
	// The equation is:
	// f(x) = delta x/2(y0 + 2*y1 + 2*y2 + ... + 2*yn-1 + yn)
	// C++ does not have a function to make the graphs.
	// I will use python to create the graphs.

	// Required:
	// Array of the data: orderludata, perludata.
	lwlis = callwli();
	
	// After calculation, it is time to write the 
	// output into text files.
	// Outputs to be written:
	// 1. elevation (lu1 orvalue, lu1 pertvalue, ...)
	// 2. distance (lu1 orvalue, lu1 pertvalue, ...)
	// 3. slope (lu1 orvalue, lu1 pertvalue, ...)
	// 4. Final Lwli values
	writeOutputs();

}


