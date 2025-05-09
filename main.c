#include <stdio.h>

int yyparse();

int main() {
    printf("Iniciando parser JaoLang...\n");
    return yyparse();
}
