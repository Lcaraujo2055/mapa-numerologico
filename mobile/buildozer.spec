[app]

title = Mapa Numerologico
package.name = mapanumerologico
package.domain = org.numerologia

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,ttf,atlas

version = 1.0

# O PDF agora é gerado por um módulo próprio, sem nenhuma dependência
# externa (mobile/simplepdf.py) — por isso não há mais reportlab/fpdf2/
# pillow aqui. plyer também foi removido (usava o mesmo mecanismo frágil
# de instalação "sem receita" via pip que causava builds instáveis); o
# compartilhamento nativo fica para uma versão futura.
# python3 e hostpython3 travados em 3.10.12 (precisam ser IGUAIS): essa é a
# combinação mais testada pela comunidade Kivy/Buildozer para Android.
# Cython travado numa versão compatível conhecida (necessário para compilar
# o próprio Kivy).
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.2.1,Cython==0.29.33

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
