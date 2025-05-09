%{
#include "jaolang.tab.h"
#include <string.h>
%}

%option noyywrap

%%

"inteirao"             { return T_INTEIRO; }
"falae"                { return T_STRING; }
"verdade_ou_farsa"     { return T_BOOL; }

"eh_tudo"              { yylval.boolean = 1; return T_TRUE; }
"eh_nada"              { yylval.boolean = 0; return T_FALSE; }

"mostra_ae"            { return T_PRINT; }
"escuta_ae_jao"        { return T_SCAN; }

"se_liga_jao"          { return T_IF; }
"se_nao_jao"           { return T_ELSE; }

"vai_rodando_ae"       { return T_FOR; }
"repete_ate_jao"       { return T_REPEAT; }
"quando"               { return T_WHEN; }

"<<"                   { return T_LBLOCK; }
">>"                   { return T_RBLOCK; }

"+"                    { return T_PLUS; }
"-"                    { return T_MINUS; }
"*"                    { return T_MULT; }
"/"                    { return T_DIV; }

"=="                   { return T_EQ; }
"<"                    { return T_LT; }
">"                    { return T_GT; }

"&&"                   { return T_AND; }
"||"                   { return T_OR; }

"vira"                 { return T_ASSIGN; }

"("                    { return T_LPAR; }
")"                    { return T_RPAR; }

[0-9]+                 { yylval.intval = atoi(yytext); return T_INT; }
\"([^\\\"]*)\"       { 
    yylval.string = strdup(yytext + 1); 
    yylval.string[strlen(yylval.string) - 1] = '\0'; 
    return T_STR; 
}

[a-zA-Z_][a-zA-Z0-9_]* { yylval.string = strdup(yytext); return T_ID; }

[ \t\r\n]+             ;
.                      { return T_UNKNOWN; }

%%
