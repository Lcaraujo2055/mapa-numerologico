# -*- coding: utf-8 -*-
"""
Salva um arquivo já gerado (no armazenamento privado do app) também na
pasta pública Downloads do Android, para que apareça no gerenciador de
arquivos e no Google Drive/outros apps.

Usa só `pyjnius` e o módulo `android` — ambos já vêm embutidos no
empacotamento padrão do Kivy para Android (nenhum requirement novo no
buildozer.spec, nenhum risco extra de build).

Se qualquer coisa falhar (aparelho/versão do Android não compatível com
alguma chamada), a função retorna None e quem chamou continua funcionando
normalmente, só sem essa cópia extra.
"""
from kivy.utils import platform


def save_to_downloads(local_path: str, filename: str):
    """Copia o arquivo em `local_path` para a pasta pública Downloads.
    Retorna uma descrição do destino em caso de sucesso, ou None se não
    conseguir (o chamador deve ter um plano B nesse caso)."""
    if platform != "android":
        return None

    try:
        with open(local_path, "rb") as f:
            data = f.read()

        from jnius import autoclass

        Build = autoclass("android.os.Build$VERSION")
        sdk_int = Build.SDK_INT

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity

        if sdk_int >= 29:
            return _save_scoped_storage(activity, data, filename)
        else:
            return _save_legacy(activity, data, filename)
    except Exception:
        return None


def _save_scoped_storage(activity, data, filename):
    """Android 10+ (API 29+): MediaStore, sem precisar de permissão."""
    from jnius import autoclass

    # Classes aninhadas do Java precisam de autoclass() próprio (com $),
    # não dá para encadear como atributo Python (ex.: MediaStore.Downloads
    # não funciona; precisa de autoclass('...MediaStore$Downloads')).
    MediaColumns = autoclass("android.provider.MediaStore$MediaColumns")
    Downloads = autoclass("android.provider.MediaStore$Downloads")
    ContentValues = autoclass("android.content.ContentValues")
    Environment = autoclass("android.os.Environment")

    resolver = activity.getContentResolver()
    values = ContentValues()
    values.put(MediaColumns.DISPLAY_NAME, filename)
    values.put(MediaColumns.MIME_TYPE, "application/pdf")
    values.put(MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)

    uri = resolver.insert(Downloads.EXTERNAL_CONTENT_URI, values)
    if uri is None:
        return None

    stream = resolver.openOutputStream(uri)
    try:
        stream.write(data)
        stream.flush()
    finally:
        stream.close()
    return f"Downloads/{filename}"


def _save_legacy(activity, data, filename):
    """Android 5–9 (API < 29): precisa de permissão e caminho público direto."""
    import os as _os
    from jnius import autoclass
    from android.permissions import request_permissions, check_permission, Permission

    if not check_permission(Permission.WRITE_EXTERNAL_STORAGE):
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
        if not check_permission(Permission.WRITE_EXTERNAL_STORAGE):
            # concessão é assíncrona; se ainda não veio, desiste desta vez
            return None

    Environment = autoclass("android.os.Environment")
    downloads_dir = Environment.getExternalStoragePublicDirectory(
        Environment.DIRECTORY_DOWNLOADS
    )
    dest_path = _os.path.join(downloads_dir.getAbsolutePath(), filename)
    with open(dest_path, "wb") as out:
        out.write(data)
    return dest_path
