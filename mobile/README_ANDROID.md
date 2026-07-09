# Mapa Numerológico — versão Android (Kivy)

Reaproveita 100% da lógica de `core.py`, `interpretations.py` e
`pdf_report.py` da versão desktop. Só a interface foi reescrita (Kivy no
lugar de CustomTkinter) e o destino do PDF passou a ser o armazenamento
privado do app + compartilhamento nativo do Android.

## Aviso importante

Este código foi escrito com cuidado seguindo padrões bem estabelecidos do
Kivy, mas **não pôde ser executado nem testado** no ambiente onde foi
gerado (sem Kivy, sem Android SDK/NDK, sem internet disponíveis ali). É
bem provável que funcione de primeira, mas se der erro no build ou algo
não aparecer certo na tela, me manda a mensagem de erro (ou um print) que
a gente ajusta — isso é normal em apps Kivy/Android na primeira rodada.

## Estrutura

```
mobile/
├── core.py              # cálculo numerológico (idêntico à versão desktop)
├── interpretations.py    # textos da Análise Interpretativa (idêntico)
├── pdf_report.py         # geração do PDF (idêntico)
├── main.py               # app Kivy: widgets, tela, eventos
├── numerologia.kv         # layout e estilo visual (navy/dourado)
├── buildozer.spec        # config do empacotamento Android
├── icon.png               # ícone provisório do app (troque à vontade)
└── .github/workflows/build-apk.yml   # build automático via GitHub Actions
```

## Caminho recomendado: GitHub Actions (não precisa de Linux/WSL local)

Como você está no Windows, este é o caminho mais direto — builda numa
máquina Linux na nuvem, de graça, sem instalar nada localmente.

1. Suba a pasta `mobile/` (com todo o conteúdo, incluindo `.github/`) para
   um repositório no GitHub.
2. Vá em **Actions** no repositório → deve aparecer o workflow "Build
   APK" rodando sozinho (ele dispara a cada push). Se não rodar
   automaticamente, use o botão **Run workflow**.
3. Espere terminar (a primeira vez demora bastante — 15 a 30 minutos,
   porque baixa o Android SDK/NDK do zero; as próximas são mais rápidas
   com cache).
4. Quando terminar, abra o run concluído → na seção **Artifacts**, baixe
   `mapa-numerologico-apk` (é um zip contendo o `.apk`).
5. Transfira o `.apk` pro celular (Google Drive, cabo USB, e-mail) e
   instale (o Android vai pedir para liberar "instalar de fontes
   desconhecidas" na primeira vez, já que não veio da Play Store).

O workflow usa a action `ArtemSBulgakov/buildozer-action`, que é a
ferramenta padrão usada pela comunidade Kivy para isso — não é mantida
pela Anthropic, então vale dar uma olhada nela antes de rodar, mas é
amplamente usada e referenciada na documentação do próprio Kivy/Buildozer.

## Alternativa: build local via WSL (Windows Subsystem for Linux)

Buildozer não roda em Windows nativo — só Linux ou macOS. No Windows, use
o WSL2 com Ubuntu:

```bash
# dentro do WSL (Ubuntu)
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev cmake libffi-dev libssl-dev
pip install --user buildozer cython

cd mobile
buildozer -v android debug
```

O `.apk` final aparece em `mobile/bin/`. A primeira build também demora
(baixa SDK/NDK) — é normal.

## Testando a interface sem gerar APK

Dá pra rodar a tela no próprio Windows/Linux/Mac antes de ir pro celular
(mais rápido para pegar erros de layout):

```bash
pip install kivy reportlab
cd mobile
python main.py
```

Isso abre o app numa janela de desktop comum — a lógica e o layout são os
mesmos, só o compartilhamento de PDF (Share sheet) só existe de fato no
Android; no desktop ele simplesmente mostra o caminho do arquivo salvo.

## O que fazer se o build falhar

Os erros mais comuns em builds Kivy/Android, e o que costumam significar:

- **Erro citando "NDK" ou "SDK license not accepted"** — normal na
  primeira vez; o Buildozer normalmente aceita sozinho
  (`android.accept_sdk_license = True` já está no `buildozer.spec`), mas
  se travar, rode `yes | buildozer android debug` no WSL.
- **Erro sobre `python-for-android` não encontrar receita de algum
  pacote** — geralmente é uma dependência que falta no `requirements` do
  `buildozer.spec`, ou uma versão que precisa ser fixada.
- **App abre e fecha na hora (crash)** — rode `buildozer android
  deploy run logcat` (com o celular conectado via USB e depuração USB
  ativada) para ver o erro real no log do Android.
- **Botão "Gerar PDF" não abre a tela de compartilhar** — é o ponto mais
  frágil deste projeto (ver abaixo). Nesse caso o app deve mostrar um
  aviso com o caminho onde o PDF foi salvo, como alternativa.

## Sobre salvar e compartilhar o PDF

O PDF é salvo em `App.user_data_dir` — uma pasta privada do app que
sempre funciona, sem precisar pedir permissão de armazenamento (esse é o
motivo de `android.permissions` estar vazio no `buildozer.spec`). Depois
de salvar, o app tenta abrir a folha nativa de compartilhamento do
Android (`plyer.share`) para você mandar o PDF para o Drive, WhatsApp,
e-mail etc. Essa parte (`plyer.share`) é a que tem mais chance de precisar
de ajuste dependendo da versão do Android/plyer — se não funcionar, o app
cai automaticamente no plano B: mostra o caminho do arquivo para você
abrir com um gerenciador de arquivos.
