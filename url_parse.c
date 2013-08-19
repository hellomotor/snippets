#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define MAX_URL_LEN (2048)
#define MAX_HOST_LEN (255)
#define DEFAULT_PORT (80)

struct url_schema {
    char host[MAX_HOST_LEN + 1];
    int port;
    char page[1786]; // max length of URL - max length of host - max length of port spe
};


struct url_schema* url_parse(const char *url) 
{
    char tmp[MAX_HOST_LEN + 6] = { 0 };
    const char *p1, *p2, *p3;
    size_t len = 0;
    struct url_schema *urls;
    
    urls = (struct url_schema *)calloc(sizeof(struct url_schema), 1);
    assert(urls);

    if (!(p1 = strstr(url, "://"))) {
        free(urls);
        return NULL;
    }
    p1 += (sizeof("://") - 1);
    if (p2 = strstr(p1, "/")) {
        const char *cp = p2 + 1;
        char *dst = urls->page;
        while (*cp)
            *dst++ = *cp++;
    }
    len = p2 ? (p2 - p1) : strlen(p1);
    assert(len < sizeof(tmp) - 1);
    strncpy(tmp, p1, len);
    if (!(p3 = strstr(tmp, ":"))) {
        strncpy(urls->host, tmp, strlen(tmp));
        urls->port = DEFAULT_PORT;
    }
    else {
        strncpy(urls->host, tmp, p3 - tmp);
        urls->port = atoi(p3 + 1);
    }
    return urls;
}


int main()
{
    //const char *url = "http://www.google.com/index.html";
    //const char *url = "http://www.google.com:8080/index/index.html";
    //
    //
    char url[1024];

    while (1) {
        printf("url: ");
        fflush(stdout);
        fgets(url, sizeof(url) - 1, stdin);

        struct url_schema *urls = url_parse(url);
        if (urls) {
            printf("host: %s\n", urls->host);
            printf("port: %d\n", urls->port);
            printf("page: %s\n", urls->page);
            free(urls);
        }
    }

    return 0;
}
