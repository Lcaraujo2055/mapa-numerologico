[app]

title = Mapa Numerologico
package.name = mapanumerologico
package.domain = org.numerologia

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,ttf,atlas

version = 1.0

# reportlab: geração do PDF. plyer: compartilhar o PDF pelo Android (Share sheet).
# python3 e hostpython3 travados em 3.11.6 (precisam ser IGUAIS): versões mais
# novas (3.13/3.14) ainda não são suportadas pelo ReportLab nem por todas as
# dependências do Kivy no Android.
requirements = python3==3.11.6,hostpython3==3.11.6,kivy==2.2.1,reportlab,plyer

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
