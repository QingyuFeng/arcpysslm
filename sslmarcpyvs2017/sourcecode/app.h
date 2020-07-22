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
-------------------------------------------------------------------------------------------------------------
** File statement:
** This app class is the class that contain all of the functions
** used in the process.
**
**
-------------------------------------------------------------------------------------------------------------
*/

// This is start of the header guard.
// ADD_H can be any unique name.  
// By convention, we use the name of the header file.
#ifndef APP_H
#define APP_H


// This is the content of the .h file, 
//	which is where the declarations go
// int add(int x, int y); // function prototype for add.h -- don't forget the semicolon!
// This is the end of the header guard

// Declare class
class App;

#define MAX_ROWS   1000000
#define MAX_COL_BYTES 1000000
#define MAX_LUIDS 100
// Declare class
class App;

#include <vector>
#include <string>
using namespace std;

// Declare class
class App;


// Declare class
class App;

// Define class
class App
{
public:
	// Constructor and distructor 
	// of the app for manage memories
	App();
	~App();

	// Variables to store the data read from
	// the asc files
	int *srclunums;
	int *sinklunums;
	
	float *ascelev;
	float *ascslope;
	float *ascdist;
	int *asclu;

	void readGisAsciiFiles();

	// Then these two will need to be combined for easier processing
	int *allsrcsinklus;


	// Define a structure to store all of the datas
	typedef struct Ludata
	{
		int luno;
		// Stores all data
		double *elevarray[MAX_LUIDS];
		double *slopearray[MAX_LUIDS];
		double *distarray[MAX_LUIDS];
		// Stores the counter
		int ludtctrarray[MAX_LUIDS];

		// stores the final number of each data value
		int finalelevctr[MAX_LUIDS];
		int finaldistctr[MAX_LUIDS];
		int finalslpctr[MAX_LUIDS];

	};

	Ludata *rawludata;
	Ludata *perludata;
	Ludata *lwlis;


	void SortCalpercent();

	void CalLWLI();

	void calAreaPercOverws();


	// Clean memory after running
	void cleanMemory();

private:

	// Functions for reading input data
	// from text files
	int *readTextInttoArray(const char *file);
	int *readArcviewInt(const char *file);
	float *readArcviewFloat(const char *file);

	int *combineSrcSinklus();

	Ludata *asc2ludata();
	void sortludata();
	Ludata *calperludata();
	Ludata *callwli();

	void removeDuplicates();

	double caltrapzarea(double olu1, double olu2, double perlu1, double perlu2);

	void writeOutputs();
	void writeElevData(const char *file);
	void writeDistData(const char *file);
	void writeSlpData(const char *file);
	void writeLwliData(const char *file);

	

	int rows;
	int cols;
	float cellsize;
	int noData;
	int noDataLu;

	int validRows[MAX_ROWS];
	double xllcorner, yllcorner;


};











#endif

