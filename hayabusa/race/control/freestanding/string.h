/* Minimal declarations for the offline V850 reference link, not a full libc. */
#ifndef RACE_FREESTANDING_STRING_H
#define RACE_FREESTANDING_STRING_H
#include <stddef.h>
void *memset(void *destination, int value, size_t count);
int memcmp(const void *left, const void *right, size_t count);
#endif
