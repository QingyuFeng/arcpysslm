#include <stdio.h>
#include <string>
#include <time.h>
#include <typeinfo>
#include <iostream>


#include "app.h"
#include "message.h"



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
#include <string>
#include <time.h>
#include <typeinfo>
#include <iostream>


#include "app.h"
#include "message.h"

App *theLWLIApp;

int main()
{

	// The first part is to set the start time of
	// the program.
	char buf[1024];
	double elapsed_time;
	time_t start, finish;

	// Get the start time:
	time(&start);
	sprintf_s(buf, sizeof buf, "Starting the program %s\n", __DATE__);

	// Define the new app class
	theLWLIApp = new App();

	// Read in the ascii input file
	theLWLIApp->readGisAsciiFiles();

	// Processing the values for Lorenz curve generation.
	// Lorenz curve needs two columns:
	// Column 1: value in decreasing order.
	// Column 2: percent of ranks (order value/total number)
	theLWLIApp->SortCalpercent();


	// After processing the data, the next step is to 
	// calculate the Trapezoidal area of the data.
	// The equation is:
	// f(x) = delta x/2(y0 + 2*y1 + 2*y2 + ... + 2*yn-1 + yn)
	// C++ does not have a function to make the graphs.
	// I will use python to create the graphs.
	theLWLIApp->CalLWLI();

	theLWLIApp->calAreaPercOverws();


	
	theLWLIApp->cleanMemory();

	time(&finish);
	elapsed_time = difftime(finish, start);

	long elapMin, elapSec, elapHour;

	elapHour = (long)(elapsed_time / 3600);
	elapMin = (long)((elapsed_time - (elapHour * 3600)) / 60);
	elapSec = (long)(elapsed_time - (elapHour * 3600) - (elapMin * 60));

	fprintf(stdout, "Runtime: %d:%02d:%02d  (Hours:Minutes:Seconds)\n", elapHour, elapMin, elapSec);

	return 0;
}

