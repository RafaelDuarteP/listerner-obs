import tkinter as tk
from tkinter import Toplevel

class CommandDocsPopup:
    @staticmethod
    def show(root):
        doc = """
Comandos que o Listener aceita via UDP:

• toggleItem<ID>
- Alterna visibilidade de um item na cena principal pela ID. Ex: toggleItem42

• transition<NOME><DURAÇÃO>
- Faz transição com nome e duração. Ex: transitionfade1000

• scene <nome> <transição> <duração> <mute> <fadeOut> <volume>
- Troca para uma cena com parâmetros opcionais. Ex: scene Cena1 fade 1000 true true 70

• toggleMute
- Alterna o mute da fonte de áudio padrão

• startRecord
- Inicia gravação

• startLive
- Inicia transmissão ao vivo

• stop
- Encerra gravação e transmissão

• setup
- Executa setup inicial

• iniciar
- Inicia transmissão padrão

• iniciarDizimo
- Inicia modo dízimo

• finalizarDizimo
- Finaliza modo dízimo

• finalizar
- Finaliza transmissão

• listItems
- Lista os itens da cena atual com sourceName e sceneItemId
"""
        top = Toplevel(root)
        top.title("Comandos Disponíveis")
        top.geometry("600x500")
        top.transient(root)
        top.grab_set()

        text = tk.Text(top, wrap="word", bg="black", fg="white", font=("Courier", 10))
        text.insert(tk.END, doc)
        text.config(state="disabled")
        text.pack(expand=True, fill="both")
