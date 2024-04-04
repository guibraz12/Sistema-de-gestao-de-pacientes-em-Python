from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Função para verificar se o CPF já existe no banco de dados
def cpf_exists(cpf):
    conn = sqlite3.connect('gestao_hospitalar.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pacientes WHERE cpf = ?', (cpf,))
    existing_patient = cursor.fetchone()  # Fetch one row
    conn.close()
    return existing_patient is not None

# Função para criar tabelas se não existirem
def create_tables():
    conn = sqlite3.connect('gestao_hospitalar.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER, 
            sexo TEXT,
            cpf TEXT UNIQUE,
            endereco TEXT,
            telefone TEXT,
            data_hora TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Verificar se é a primeira solicitação e criar tabelas
@app.before_request
def before_request():
    create_tables()

# Criando a rota base
@app.route('/')
def index():
    conn = sqlite3.connect('gestao_hospitalar.db')
    cursor = conn.cursor() 
    cursor.execute('SELECT * FROM pacientes')
    pacientes = cursor.fetchall()
    conn.close()
    return render_template('index.html', pacientes=pacientes)

# Criando a rota /novo_paciente
@app.route('/novo_paciente', methods=['GET', 'POST'])
def novo_paciente():
    if request.method == "POST":
        nome = request.form['nome']
        idade = request.form['idade']
        sexo = request.form['sexo']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        
        # Verificar se o CPF já existe no banco de dados
        if cpf_exists(cpf):
            return '''
            <script>
                alert("CPF já está em uso. Por favor, insira um CPF diferente.");
                window.location = "/novo_paciente"; // Redirecionar de volta para a página de adicionar novo paciente
            </script>
            '''
        
        # Capturar a data e hora atual
        data_hora_atual = datetime.now().strftime("(%d/%m/%y) | %H:%M:%S")

        # Conectar ao banco de dados e inserir novo paciente
        conn = sqlite3.connect('gestao_hospitalar.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pacientes (nome, idade, sexo, cpf, endereco, telefone, data_hora)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, idade, sexo, cpf, endereco, telefone, data_hora_atual))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('novo_paciente.html')

# Criando a 'rota' /limpar_pacientes
@app.route('/limpar_pacientes')
def limpar_pacientes():
    conn = sqlite3.connect('gestao_hospitalar.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pacientes')
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Rodando o app
if __name__ == "__main__":
    app.run(debug=True)
