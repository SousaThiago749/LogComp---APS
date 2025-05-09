%{
#include <stdio.h>
#include <stdlib.h>

int yylex();
void yyerror(const char *s);
%}

%union {
    int intval;
    char* string;
    int boolean;
}

%token T_INTEIRO T_STRING T_BOOL
%token T_TRUE T_FALSE
%token T_PRINT T_SCAN
%token T_IF T_ELSE
%token T_FOR T_REPEAT T_WHEN
%token T_LBLOCK T_RBLOCK
%token T_PLUS T_MINUS T_MULT T_DIV
%token T_EQ T_LT T_GT
%token T_AND T_OR
%token T_ASSIGN
%token T_LPAR T_RPAR
%token <intval> T_INT
%token <string> T_STR
%token <string> T_ID
%token T_UNKNOWN

%%

programa:
    T_LBLOCK lista_comandos T_RBLOCK
    ;

lista_comandos:
    comando
    | lista_comandos comando
    ;

comando:
      declaracao
    | atribuicao
    | comando_condicional
    | comando_repeticao
    | comando_repeticao_nova
    | comando_saida
    | comando_entrada
    ;

declaracao:
    tipo T_ID T_ASSIGN expressao
    | tipo T_ID
    ;

atribuicao:
    T_ID T_ASSIGN expressao
    ;

comando_condicional:
    T_IF expressao bloco T_ELSE bloco
    | T_IF expressao bloco
    ;

comando_repeticao:
    T_FOR expressao bloco
    ;

comando_repeticao_nova:
    T_REPEAT bloco T_WHEN expressao
    ;

comando_saida:
    T_PRINT T_LPAR expressao T_RPAR
    ;

comando_entrada:
    T_SCAN T_LPAR T_RPAR
    ;

bloco:
    T_LBLOCK lista_comandos T_RBLOCK
    ;

tipo:
      T_INTEIRO
    | T_STRING
    | T_BOOL
    ;

expressao:
    expressao T_PLUS termo
    | expressao T_MINUS termo
    | expressao T_EQ termo
    | expressao T_LT termo
    | expressao T_GT termo
    | expressao T_AND termo
    | expressao T_OR termo
    | termo
    ;

termo:
    termo T_MULT fator
    | termo T_DIV fator
    | fator
    ;

fator:
      T_INT
    | T_STR
    | T_TRUE
    | T_FALSE
    | T_ID
    | T_LPAR expressao T_RPAR
    | comando_entrada
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Erro: %s\n", s);
}