#include <stdio.h>

void DisplayMessage(char const *s1, char const *s2, int line)
{
	if (s1 == NULL)
	{
		fprintf(stdout, "No message\n");
		return;
	}
	if (s2)
		fprintf(stdout, "Message: %s\n    %s %d\n", s1, s2, line);
	else
		fprintf(stdout, "%s\n", s1);

}