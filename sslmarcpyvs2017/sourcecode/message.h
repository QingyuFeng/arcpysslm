// This is start of the header guard.
// ADD_H can be any unique name.  
// By convention, we use the name of the header file.
#ifndef message_h
#define message_h

// This is the content of the .h file, 
//	which is where the declarations go
// int add(int x, int y); // function prototype for add.h -- don't forget the semicolon!

// This is the end of the header guard

void DisplayMessage(const char *m1, const char *m2 = 0, int line = 0);
void fatalError(const char *msg);





#endif