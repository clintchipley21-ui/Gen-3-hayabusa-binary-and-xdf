#include "string.h"
void *memset(void *destination, int value, size_t count) {
    unsigned char *p=destination;
    while (count--) *p++=(unsigned char)value;
    return destination;
}
int memcmp(const void *left, const void *right, size_t count) {
    const unsigned char *l=left, *r=right;
    while (count--) {
        if (*l != *r) return *l < *r ? -1 : 1;
        ++l; ++r;
    }
    return 0;
}
