[app]

title = Mapa Numerologico
package.name = mapanumerologico
package.domain = org.numerologia

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,ttf,atlas

version = 1.0

# fpdf2: geração do PDF (Python puro, sem código C — evita o problema da
# receita travada do reportlab no python-for-android). fpdf2 depende do
# Pillow (que TEM código C) — por isso "pillow" precisa estar explícito
# aqui, para o Buildozer compilá-lo com a receita própria dele em vez de
# tentar (e falhar) baixar um wheel pronto para Android via pip.
# plyer: compartilhar o PDF pelo Android (Share sheet).
# python3 e hostpython3 travados em 3.10.12 (precisam ser IGUAIS): essa é a
# combinação mais testada pela comunidade Kivy/Buildozer para Android;
# 3.11+ tem apresentado um bug conhecido de "pip" corrompido durante o build.
# Cython travado numa versão compatível conhecida.
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.2.1,pillow,fpdf2,plyer,Cython==0.29.33

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png
# ^ ícone provisório (navy/dourado, letra N) — troque por outro icon.png 512x512 quando quiser.

# Sem permissões especiais: o PDF é salvo no diretório privado do app
# (App.user_data_dir) e compartilhado via content:// (plyer/FileProvider),
# então não precisa de WRITE_EXTERNAL_STORAGE nem pedir permissão em runtime.
android.permissions =

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
