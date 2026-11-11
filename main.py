from core.persistencia import inicializar_archivos
from views.app import TallerApp

def main():
    inicializar_archivos()
    app = TallerApp()
    app.mainloop()

if __name__ == "__main__":
    main()