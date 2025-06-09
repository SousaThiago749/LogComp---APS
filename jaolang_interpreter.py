import sys

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

class SymbolTable:
    def __init__(self, parent=None):
        self.table = {}
        self.parent = parent

    def declare(self, key, type_, value=None, is_func=False):
        if key in self.table:
            raise Exception(f"Variável ou função '{key}' já declarada.")
        self.table[key] = {"type": type_, "value": value, "is_func": is_func}

    def get(self, key):
        if key in self.table:
            return self.table[key]["value"], self.table[key]["type"], self.table[key].get("is_func", False)
        elif self.parent:
            return self.parent.get(key)
        raise Exception(f"Variável ou função '{key}' não encontrada.")

    def set(self, key, value, type_):
        if key in self.table:
            if self.table[key]["type"] != type_:
                raise Exception(f"Tipo incompatível: '{type_}' != '{self.table[key]['type']}'")
            self.table[key]["value"] = value
            return
        elif self.parent:
            self.parent.set(key, value, type_)
            return
        raise Exception(f"Variável '{key}' não declarada.")


class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children or []

    def Evaluate(self, st):
        if self.value == "BLOCK":
            for child in self.children:
                res = child.Evaluate( SymbolTable(st) if child.value=="BLOCK" else st )

                # se algum filho devolveu algo (foi um RETURN em qualquer profundidade),
                # propague imediatamente
                if res is not None:
                    return res
            return None

        if self.value == "PRINT":
            val, typ = self.children[0].Evaluate(st)
            # booleanos em minúscula
            if typ == "bool":
                print("true" if val else "false")
            else:
                print(val)
            return None

        if self.value == "ASSIGN":
            varName = self.children[0].value
            val, typ = self.children[1].Evaluate(st)
            st.set(varName, val, typ)
            return None

        if self.value == "VAR_DECL":
            varName = self.children[0].value
            varType = self.children[1].value
            if len(self.children) == 3:
                val, valType = self.children[2].Evaluate(st)
                if varType != valType:
                    raise Exception("Tipo da atribuição incompatível com declaração.")
                st.declare(varName, varType, val)
            else:
                default = 0 if varType == "int" else "" if varType == "string" else False
                st.declare(varName, varType, default)
            return None

        if self.value == "IF":
            cond, typ = self.children[0].Evaluate(st)
            if typ != "bool":
                raise Exception("Condicional do IF precisa ser bool.")
            if cond:
                return self.children[1].Evaluate(st)
            elif len(self.children) == 3:
                return self.children[2].Evaluate(st)
            return None

        if self.value == "FOR":
            while True:
                cond, typ = self.children[0].Evaluate(st)
                if typ != "bool":
                    raise Exception("Condicional do FOR precisa ser bool.")
                if not cond:
                    break
                self.children[1].Evaluate(st)
        
        if self.value == "REPEAT":
            block, cond = self.children
            while True:
                block.Evaluate(st)
                c, t = cond.Evaluate(st)
                if t != "bool":
                    raise Exception("Condicional do REPEAT precisa ser bool.")
                if not c:
                    break
            return None

        if self.value == "SCAN":
            val = input()
            try:
                return int(val), "int"
            except:
                return val, "string"

        if isinstance(self.value, str) and not self.children:
            val, typ, _ = st.get(self.value)   # ignora is_func
            return val, typ

        return None

class IntVal(Node):
    def Evaluate(self, st):
        return self.value, "int"

class BoolVal(Node):
    def Evaluate(self, st):
        return self.value, "bool"

class StringVal(Node):
    def Evaluate(self, st):
        return self.value, "string"

def to_str(val, typ):
    if typ == "bool":
        return "true" if val else "false"
    return str(val)

class BinOp(Node):
    def Evaluate(self, st):
        lval, ltype = self.children[0].Evaluate(st)
        rval, rtype = self.children[1].Evaluate(st)

        # '+' (concatena strings ou soma ints)
        if self.value == "+":
            if ltype=="string" or rtype=="string":
                return to_str(lval, ltype) + to_str(rval, rtype), "string"
            if ltype==rtype=="int":
                return lval + rval, "int"
            raise Exception("Operação '+' inválida para tipos diferentes.")

        # '-' só em inteiros
        elif self.value == "-":
            if ltype==rtype=="int":
                return lval - rval, "int"
            raise Exception("Operação '-' requer inteiros.")

        # '*' só em inteiros
        elif self.value == "*":
            if ltype==rtype=="int":
                return lval * rval, "int"
            raise Exception("Operação '*' requer inteiros.")

        # '/' só em inteiros (e checa divisão por zero)
        elif self.value == "/":
            if ltype==rtype=="int":
                if rval == 0:
                    raise Exception("Divisão por zero.")
                return lval // rval, "int"
            raise Exception("Operação '/' requer inteiros.")

        # relacional '<' e '>'  
        elif self.value in ("<",">"):
            # ints OK
            if ltype==rtype=="int":
                return (lval < rval if self.value=="<" else lval > rval), "bool"
            # strings lex order OK
            if ltype==rtype=="string":
                return (lval < rval if self.value=="<" else lval > rval), "bool"
            raise Exception(f"Operação '{self.value}' requer inteiros ou strings.")

        # igualdade '==' só entre mesmos tipos
        elif self.value == "==":
            if ltype != rtype:
                raise Exception(f"Não é possível comparar '{ltype}' com '{rtype}'.")
            return (lval == rval), "bool"

        # '&&' / '||' só em booleanos
        elif self.value in ("&&","||"):
            if ltype==rtype=="bool":
                return (lval and rval if self.value=="&&" else lval or rval), "bool"
            raise Exception(f"Operação '{self.value}' requer booleanos.")

        raise Exception(f"Operador desconhecido: {self.value}")

class Return(Node):
    def __init__(self, expr):
        super().__init__("RETURN", [expr])

    def Evaluate(self, st):
        return self.children[0].Evaluate(st)

class UnOp(Node):
    def Evaluate(self, st):
        val, typ = self.children[0].Evaluate(st)
        if self.value == "-":
            if typ!="int": raise Exception("Unário '-' só em int.")
            return -val, "int"
        if self.value == "+":
            return val, typ 
        if self.value == "!":
            if typ!="bool": raise Exception("Unário '!' só em bool.")
            return not val, "bool"
        return val, typ

class NoOp(Node):
    def Evaluate(self, st):
        return None


class FuncDec(Node):
    def __init__(self, name, params, return_type, body):
        super().__init__("FUNC_DEC", [body])
        self.name = name
        self.params = params  # lista de tuplas: (nome, tipo)
        self.return_type = return_type

    def Evaluate(self, st):
        st.declare(self.name, self.return_type, self, is_func=True)


class FuncCall(Node):
    def __init__(self, name, args):
        super().__init__("FUNC_CALL", args)
        self.name = name

    def Evaluate(self, st):

        if self.name == "Println":
            for arg in self.children:
                val, typ = arg.Evaluate(st)
                print("true" if typ == "bool" else val)
            return None
        
        val, typ, is_func = st.get(self.name)
        if not is_func:
            raise Exception(f"'{self.name}' não é uma função.")
        func_node = val  # é um FuncDec
        if len(func_node.params) != len(self.children):
            raise Exception("Número incorreto de argumentos.")
        
        local_st = SymbolTable(st)
        for (pname, ptype), arg_expr in zip(func_node.params, self.children):
            arg_val, arg_type = arg_expr.Evaluate(st)
            if arg_type != ptype:
                raise Exception(f"Tipo incompatível em argumento '{pname}': esperado {ptype}, recebido {arg_type}")
            local_st.declare(pname, ptype, arg_val)
        
        result = func_node.children[0].Evaluate(local_st)

        # --- NOVO BLOCO DE VERIFICAÇÃO --------------------------
        if isinstance(result, tuple):           # houve "return expr"
            ret_val, ret_type = result

            # função declarada void não pode retornar valor
            if func_node.return_type == "void":
                raise Exception(f"Função '{self.name}' é void — não pode retornar valor.")

            # tipo incompatível
            if ret_type != func_node.return_type:
                raise Exception(f"Retorno de '{self.name}' incompatível "
                                f"({ret_type} ≠ {func_node.return_type})")

            return result                       # tudo certo

        # não houve return explícito
        if func_node.return_type != "void":
            raise Exception(f"Função '{self.name}' deve retornar '{func_node.return_type}'.")

        return None 



class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

class Tokenizer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.actual = None
        self.selectNext()

    def selectNext(self):
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

        if self.position >= len(self.source):
            self.actual = Token("EOF", None)
            return

        s = self.source[self.position:]

        if s.startswith("//"):
            while self.position < len(self.source) and self.source[self.position] != '\n':
                self.position += 1
            self.selectNext()
            return

        keywords = [
            "inteirao",         # tipo inteiro
            "falae",            # tipo string
            "verdade_ou_farsa", # tipo bool

            "eh_tudo",          # true
            "eh_nada",          # false

            "mostra_ae",        # print
            "escuta_ae_jao",    # scan

            "se_liga_jao",      # if
            "se_nao_jao",       # else

            "vai_rodando_ae",   # for
            "repete_ate_jao",   # repeat…when
            "quando",           # when (para o repeat)
            "vira",
        ]
        for kw in keywords:
            if s.startswith(kw) and (len(s)==len(kw) or not s[len(kw)].isalnum()):
                if kw == "inteirao":
                    self.actual = Token("T_INTEIRO", kw)
                elif kw == "falae":
                    self.actual = Token("T_STRING", kw)
                elif kw == "verdade_ou_farsa":
                    self.actual = Token("T_BOOL", kw)
                elif kw == "eh_tudo":
                    self.actual = Token("T_TRUE", True)
                elif kw == "eh_nada":
                    self.actual = Token("T_FALSE", False)
                elif kw == "mostra_ae":
                    self.actual = Token("T_PRINT", kw)
                elif kw == "escuta_ae_jao":
                    self.actual = Token("T_SCAN", kw)
                elif kw == "se_liga_jao":
                    self.actual = Token("T_IF", kw)
                elif kw == "se_nao_jao":
                    self.actual = Token("T_ELSE", kw)
                elif kw == "vai_rodando_ae":
                    self.actual = Token("T_FOR", kw)
                elif kw == "repete_ate_jao":
                    self.actual = Token("T_REPEAT", kw)
                elif kw == "quando":
                    self.actual = Token("T_WHEN", kw)
                elif kw == "vira":
                    self.actual = Token("T_ASSIGN", kw)
                self.position += len(kw)
                return
                

        for op, name in {"<<":"T_LBLOCK", ">>":"T_RBLOCK", "==":"T_EQ", "&&":"T_AND", "||":"T_OR"}.items():
            if s.startswith(op):
                self.actual = Token(name, op)
                self.position += len(op)
                return

        single = {
            '+': "PLUS", '-': "MINUS", '*': "MULT", '/': "DIV",
            '=': "EQUAL", '(': "LPAR", ')': "RPAR", '{': "LB", '}': "RB",
            '<': "LT", '>': "GT", '!': "NOT", ',': "COMMA"
        }
        if self.source[self.position] in single:
            self.actual = Token(single[self.source[self.position]], self.source[self.position])
            self.position += 1
            return

        if self.source[self.position] == '"':
            self.position += 1
            val = ""
            while self.position < len(self.source) and self.source[self.position] != '"':
                val += self.source[self.position]
                self.position += 1
            if self.position == len(self.source):
                raise Exception("String malformada.")
            self.position += 1  # fecha aspas
            self.actual = Token("STRING", val)
            return

        if self.source[self.position].isdigit():
            num = ""
            while self.position < len(self.source) and self.source[self.position].isdigit():
                num += self.source[self.position]
                self.position += 1
            self.actual = Token("INT", int(num))
            return

        if self.source[self.position].isalpha() or self.source[self.position] == '_':
            ident = ""
            while (self.position < len(self.source) and
                   (self.source[self.position].isalnum() or self.source[self.position] == '_')):
                ident += self.source[self.position]
                self.position += 1
            self.actual = Token("IDEN", ident)
            return

        raise Exception(f"Caractere inválido: {self.source[self.position]}")

class Parser:
    @staticmethod
    def run(code):
        tokenizer = Tokenizer(code)
        Parser.tokenizer = tokenizer
        res = Parser.parseProgram()
        if Parser.tokenizer.actual.type != "EOF":
            raise Exception("Erro: tokens restantes após o fim.")
        return res

    @staticmethod
    def parseBlock():
        if Parser.tokenizer.actual.type != "T_LBLOCK":
            raise Exception("Esperado '<<'")
        Parser.tokenizer.selectNext()        # consome <<
        stmts = []
        while Parser.tokenizer.actual.type != "T_RBLOCK":
            stmts.append(Parser.parseStatement())
        Parser.tokenizer.selectNext()        # consome >>
        return Node("BLOCK", stmts)

    @staticmethod
    def parseStatement():
        t = Parser.tokenizer.actual.type

        # 1) declaração de variável: inteirao|falae|verdade_ou_farsa ID vira expr?
        if t in ("T_INTEIRO", "T_STRING", "T_BOOL"):
            typ = t
            Parser.tokenizer.selectNext()  # consome o tipo
            if Parser.tokenizer.actual.type != "IDEN":
                raise Exception("Esperado nome de variável após o tipo")
            name = Parser.tokenizer.actual.value
            Parser.tokenizer.selectNext()  # consome o identificador

            # monta nó VAR_DECL: [nome, tipo_str, (expr)?]
            tipo_str = {"T_INTEIRO":"int", "T_STRING":"string", "T_BOOL":"bool"}[typ]
            children = [ Node(name), Node(tipo_str) ]
            if Parser.tokenizer.actual.type == "T_ASSIGN":
                Parser.tokenizer.selectNext()  # consome 'vira'
                children.append(Parser.parseBExpression())
            return Node("VAR_DECL", children)

        # 2) repete_ate_jao << bloco >> quando (cond)
        elif t == "T_REPEAT":
            Parser.tokenizer.selectNext()          # consome 'repete_ate_jao'
            body = Parser.parseBlock()             # lê << … >>
            if Parser.tokenizer.actual.type != "T_WHEN":
                raise Exception("Esperado 'quando' após bloco do 'repete_ate_jao'")
            Parser.tokenizer.selectNext()          # consome 'quando'
            cond = Parser.parseBExpression()
            return Node("REPEAT", [body, cond])

        # 3) se_liga_jao cond << … >> [se_nao_jao << … >>]
        elif t == "T_IF":
            Parser.tokenizer.selectNext()          # consome 'se_liga_jao'
            cond = Parser.parseBExpression()
            then_blk = Parser.parseBlock()
            if Parser.tokenizer.actual.type == "T_ELSE":
                Parser.tokenizer.selectNext()      # consome 'se_nao_jao'
                else_blk = Parser.parseBlock()
                return Node("IF", [cond, then_blk, else_blk])
            return Node("IF", [cond, then_blk])

        # 4) vai_rodando_ae cond << … >>
        elif t == "T_FOR":
            Parser.tokenizer.selectNext()          # consome 'vai_rodando_ae'
            cond = Parser.parseBExpression()
            blk = Parser.parseBlock()
            return Node("FOR", [cond, blk])

        # 5) mostra_ae(expr)
        elif t == "T_PRINT":
            Parser.tokenizer.selectNext()          # consome 'mostra_ae'
            if Parser.tokenizer.actual.type != "LPAR":
                raise Exception("Esperado '(' após 'mostra_ae'")
            Parser.tokenizer.selectNext()
            expr = Parser.parseBExpression()
            if Parser.tokenizer.actual.type != "RPAR":
                raise Exception("Esperado ')' após expressão de print")
            Parser.tokenizer.selectNext()
            return Node("PRINT", [expr])

        # 6) identificador: atribuição (vira) ou chamada de função
        elif t == "IDEN":
            name = Parser.tokenizer.actual.value
            Parser.tokenizer.selectNext()
            # chamada de função: nome(arg, …)
            if Parser.tokenizer.actual.type == "LPAR":
                Parser.tokenizer.selectNext()
                args = []
                if Parser.tokenizer.actual.type != "RPAR":
                    args.append(Parser.parseBExpression())
                    while Parser.tokenizer.actual.type == "COMMA":
                        Parser.tokenizer.selectNext()
                        args.append(Parser.parseBExpression())
                if Parser.tokenizer.actual.type != "RPAR":
                    raise Exception("Esperado ')' na chamada de função")
                Parser.tokenizer.selectNext()
                return FuncCall(name, args)
            # atribuição: nome vira expr
            if Parser.tokenizer.actual.type == "T_ASSIGN":
                Parser.tokenizer.selectNext()
                return Node("ASSIGN", [Node(name), Parser.parseBExpression()])
            raise Exception("Esperado 'vira' ou chamada de função após identificador")

        # 7) bloco aninhado: << … >>
        elif t == "T_LBLOCK":
            return Parser.parseBlock()

        else:
            raise Exception(f"Token inesperado na instrução: {t}")

    @staticmethod
    def parseBExpression():
        node = Parser.parseBTerm()
        while Parser.tokenizer.actual.type == "T_OR":
            Parser.tokenizer.selectNext()
            node = BinOp("||", [node, Parser.parseBTerm()])
        return node

    @staticmethod
    def parseBTerm():
        node = Parser.parseRelExpression()
        while Parser.tokenizer.actual.type == "T_AND":
            Parser.tokenizer.selectNext()
            node = BinOp("&&", [node, Parser.parseRelExpression()])
        return node

    @staticmethod
    def parseRelExpression():
        node = Parser.parseExpression()
        while Parser.tokenizer.actual.type in ("LT", "GT", "T_EQ"):
            op = Parser.tokenizer.actual.type
            Parser.tokenizer.selectNext()
            right = Parser.parseExpression()
            op_map = {"LT":"<", "GT":">", "T_EQ":"=="}
            node = BinOp(op_map[op], [node, right])
        return node

    @staticmethod
    def parseExpression():
        node = Parser.parseTerm()
        while Parser.tokenizer.actual.type in ("PLUS", "MINUS"):
            op = Parser.tokenizer.actual.type
            Parser.tokenizer.selectNext()
            node = BinOp("+" if op == "PLUS" else "-", [node, Parser.parseTerm()])
        return node

    @staticmethod
    def parseTerm():
        node = Parser.parseFactor()
        while Parser.tokenizer.actual.type in ("MULT", "DIV"):
            op = Parser.tokenizer.actual.type
            Parser.tokenizer.selectNext()
            node = BinOp("*" if op == "MULT" else "/", [node, Parser.parseFactor()])
        return node

    @staticmethod
    def parseFactor():
        # 1) consome zero ou mais unários
        unaries = []
        while Parser.tokenizer.actual.type in ("PLUS","MINUS","NOT"):
            unaries.append(Parser.tokenizer.actual.type)
            Parser.tokenizer.selectNext()

        # 2) parsing base
        token = Parser.tokenizer.actual
        if token.type == "INT":
            node = IntVal(token.value)
        elif token.type == "STRING":
            node = StringVal(token.value)
        elif token.type in ("T_TRUE","T_FALSE"):
            node = BoolVal(token.value)
        elif token.type == "LPAR":
            Parser.tokenizer.selectNext()
            node = Parser.parseBExpression()
            if Parser.tokenizer.actual.type != "RPAR":
                raise Exception("Esperado ')'")
            Parser.tokenizer.selectNext()  # consome ')'
            # importante: já sai aqui, não faz selectNext de novo depois
        elif token.type == "T_SCAN":
            Parser.tokenizer.selectNext()        # consome escuta_ae_jao
            if Parser.tokenizer.actual.type != "LPAR":
                raise Exception("Esperado '(' após escuta_ae_jao")
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.actual.type != "RPAR":
                raise Exception("Esperado ')' após escuta_ae_jao(")
            Parser.tokenizer.selectNext()
            node = Node("SCAN", [])
        elif token.type == "IDEN":
            name = token.value
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.actual.type == "LPAR":
                # chamada de função
                Parser.tokenizer.selectNext()
                args = []
                if Parser.tokenizer.actual.type != "RPAR":
                    args.append(Parser.parseBExpression())
                    while Parser.tokenizer.actual.type == "COMMA":
                        Parser.tokenizer.selectNext()
                        args.append(Parser.parseBExpression())
                if Parser.tokenizer.actual.type != "RPAR":
                    raise Exception("Esperado ')' na chamada de função")
                Parser.tokenizer.selectNext()
                node = FuncCall(name, args)
            else:
                node = Node(name)
        else:
            raise Exception(f"Token inesperado no fator: {token.type}")

        # 3) só avança se ainda não fez isso acima (evita pular token extra)
        if token.type not in ("LPAR", "SCAN", "IDEN"):
            Parser.tokenizer.selectNext()

        # 4) aninha unários
        for u in reversed(unaries):
            if u == "NOT":
                node = UnOp("!", [node])
            elif u == "MINUS":
                node = UnOp("-", [node])
            elif u == "PLUS":
                node = UnOp("+", [node])
        return node

    
    @staticmethod
    def parseProgram():
        return Parser.parseBlock()
    
    @staticmethod
    def parseFuncDeclaration():
        Parser.tokenizer.selectNext()  # consome 'func'

        if Parser.tokenizer.actual.type != "IDEN":
            raise Exception("Esperado nome da função")
        name = Parser.tokenizer.actual.value
        Parser.tokenizer.selectNext()

        if Parser.tokenizer.actual.type != "LPAR":
            raise Exception("Esperado '(' após nome da função")
        Parser.tokenizer.selectNext()

        params = []
        while Parser.tokenizer.actual.type != "RPAR":
            if Parser.tokenizer.actual.type != "IDEN":
                raise Exception("Esperado nome do parâmetro")
            pname = Parser.tokenizer.actual.value
            Parser.tokenizer.selectNext()

            if Parser.tokenizer.actual.type != "IDEN":
                raise Exception("Esperado tipo do parâmetro")
            ptype = Parser.tokenizer.actual.value
            Parser.tokenizer.selectNext()

            params.append((pname, ptype))

            if Parser.tokenizer.actual.type == "COMMA":
                Parser.tokenizer.selectNext()
            elif Parser.tokenizer.actual.type != "RPAR":
                raise Exception("Esperado ',' ou ')'")

        Parser.tokenizer.selectNext()  # consome ')'

        if Parser.tokenizer.actual.type == "IDEN":
            return_type = Parser.tokenizer.actual.value
            Parser.tokenizer.selectNext()
        else:
            return_type = "void"

        body = Parser.parseBlock()

        return FuncDec(name, params, return_type, body)



def main():
    if len(sys.argv) != 2: sys.exit(1)
    source = open(sys.argv[1], encoding='utf-8').read()
    ast = Parser.run(source)
    st = SymbolTable()
    ast.Evaluate(st)


if __name__ == "__main__":
    main()
