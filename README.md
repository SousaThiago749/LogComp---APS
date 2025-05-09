# APS - Linguagem de Programação "JaoLang"

# Resumo da Linguagem

* **Declarações** de variáveis diretas: tipo + nome.
* **Tipos suportados:**

  * `inteirao` → `int`
  * `falae` → `string`
  * `verdade_ou_farsa` → `bool`
* **Valores booleanos:**

  * `eh_tudo` → `true`
  * `eh_nada` → `false`
* **Entrada/Saída:**

  * `mostra_ae(expr)` → print
  * `escuta_ae_jao()` → input
* **Controle de Fluxo:**

  * `se_liga_jao expr << bloco >> [ se_nao_jao << bloco >> ]`
  * `vai_rodando_ae expr << bloco >>`
  * `repete_ate_jao << bloco >> quando expr`
* **Operadores suportados:**

  * Aritméticos: `+`, `-`, `*`, `/`
  * Relacionais: `==`, `<`, `>`
  * Lógicos: `&&`, `||`
  * Atribuição: `vira` (em vez de `=`)

---

# Definição Formal (EBNF)

```ebnf
<programa> ::= "<<" <lista_de_comandos> ">>"

<lista_de_comandos> ::= <comando> { <comando> }

<comando> ::= <declaracao> 
            | <atribuicao> 
            | <comando_condicional> 
            | <comando_repeticao> 
            | <comando_repeticao_nova>
            | <comando_saida>
            | <comando_entrada>

<declaracao> ::= <tipo> <identificador> [ "vira" <expressao> ]

<atribuicao> ::= <identificador> "vira" <expressao>

<comando_condicional> ::= "se_liga_jao" <expressao> <bloco> [ "se_nao_jao" <bloco> ]

<comando_repeticao> ::= "vai_rodando_ae" <expressao> <bloco>

<comando_repeticao_nova> ::= "repete_ate_jao" <bloco> "quando" <expressao>

<comando_saida> ::= "mostra_ae" "(" <expressao> ")"

<comando_entrada> ::= "escuta_ae_jao" "(" ")"

<bloco> ::= "<<" <lista_de_comandos> ">>"

<tipo> ::= "inteirao" | "falae" | "verdade_ou_farsa"

<expressao> ::= <termo> { ("+" | "-") <termo> }

<termo> ::= <fator> { ("*" | "/") <fator> }

<fator> ::= <inteiro> 
          | <string> 
          | <booleano> 
          | <identificador> 
          | "(" <expressao> ")"
          | <comando_entrada>

<booleano> ::= "eh_tudo" | "eh_nada"

<identificador> ::= (* uma letra seguida por letras ou dígitos *)

<inteiro> ::= (* sequência de dígitos *)

<string> ::= (* sequência de caracteres entre aspas *)
```

---

# Exemplo de Programa

```plaintext
<<
    inteirao idade vira 18
    falae nome vira "Jaozinho"
    verdade_ou_farsa ta_firmasso vira eh_tudo

    mostra_ae(idade)
    mostra_ae(nome)

    se_liga_jao idade > 17 <<
        mostra_ae("Pode tirar carta!")
    >> se_nao_jao <<
        mostra_ae("Vai crescer primeiro, parça!")
    >>

    vai_rodando_ae idade < 21 <<
        idade vira idade + 1
        mostra_ae(idade)
    >>

    repete_ate_jao <<
        idade vira idade + 2
        mostra_ae(idade)
    >> quando idade < 30
>>
```
