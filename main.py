from core.persistencia import inicializar_archivos
from views.app import TallerApp

if __name__ == "__main__":
    inicializar_archivos()
    app = TallerApp()
    app.mainloop()