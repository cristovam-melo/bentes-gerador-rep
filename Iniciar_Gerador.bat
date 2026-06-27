@echo off
echo ========================================================
echo        BENTES - GERADOR DE REGISTRO DE PROJETOS
echo ========================================================
echo.
echo Iniciando o sistema... Por favor, aguarde.
echo O seu navegador sera aberto automaticamente.
echo.
echo (Para fechar o sistema depois de usar, basta fechar esta janela preta)
echo.

call venv\Scripts\activate
streamlit run app.py

pause
