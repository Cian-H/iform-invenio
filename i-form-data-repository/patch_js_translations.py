import glob
import os
import shutil
import json

def main():
    # 1. Ensure ga directories exist and have translations.json
    packages = [
        'invenio_communities',
        'invenio_search_ui',
        'invenio_app_rdm',
        'invenio_requests',
        'invenio_jobs',
        'invenio_rdm_records',
        'invenio_administration'
    ]
    bases = [
        '/opt/invenio/src/.venv/lib/python3.12/site-packages',
        '/opt/invenio/var/instance/assets/translations'
    ]
    for pkg in packages:
        for base in bases:
            for root, dirs, files_in_dir in os.walk(base):
                if root.endswith('messages') and pkg in root:
                    ga_dir = os.path.join(root, 'ga')
                    os.makedirs(ga_dir, exist_ok=True)
                    json_path = os.path.join(ga_dir, 'translations.json')
                    if not os.path.exists(json_path) or os.path.getsize(json_path) <= 2:
                        with open(json_path, 'w') as fp:
                            fp.write('{}')
                        print(f"Created empty translations.json: {json_path}")

    # 2. Copy the actual compiled translations if they exist
    copies = [
        (
            '/opt/invenio/src/.venv/lib/python3.12/site-packages/invenio_communities/assets/semantic-ui/translations/invenio_communities/messages/ga/translations.json',
            '/opt/invenio/var/instance/assets/translations/invenio_communities/messages/ga/translations.json'
        ),
        (
            '/opt/invenio/src/.venv/lib/python3.12/site-packages/invenio_search_ui/assets/semantic-ui/translations/invenio_search_ui/messages/ga/translations.json',
            '/opt/invenio/var/instance/assets/translations/invenio_search_ui/messages/ga/translations.json'
        )
    ]
    for src, dst in copies:
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"Copied compiled translations: {src} -> {dst}")

    # 3. Extract app_rdm translations from global ga.json
    global_ga = '/opt/invenio/var/instance/translations/ga.json'
    app_rdm_dst = '/opt/invenio/var/instance/assets/translations/invenio_app_rdm/messages/ga/translations.json'
    if os.path.exists(global_ga):
        try:
            with open(global_ga, 'r') as fp:
                ga_data = json.load(fp)
            app_rdm_data = ga_data.get('invenio_app_rdm', {})
            os.makedirs(os.path.dirname(app_rdm_dst), exist_ok=True)
            with open(app_rdm_dst, 'w') as fp:
                json.dump(app_rdm_data, fp, indent=2)
            print(f"Extracted invenio_app_rdm translations to {app_rdm_dst}")
            
            # Also extract search_ui and communities if they were not copied
            search_ui_dst = '/opt/invenio/var/instance/assets/translations/invenio_search_ui/messages/ga/translations.json'
            if 'invenio_search_ui' in ga_data:
                os.makedirs(os.path.dirname(search_ui_dst), exist_ok=True)
                with open(search_ui_dst, 'w') as fp:
                    json.dump(ga_data['invenio_search_ui'], fp, indent=2)
                print(f"Extracted invenio_search_ui translations to {search_ui_dst}")
                
            communities_dst = '/opt/invenio/var/instance/assets/translations/invenio_communities/messages/ga/translations.json'
            if 'invenio_communities' in ga_data:
                os.makedirs(os.path.dirname(communities_dst), exist_ok=True)
                with open(communities_dst, 'w') as fp:
                    json.dump(ga_data['invenio_communities'], fp, indent=2)
                print(f"Extracted invenio_communities translations to {communities_dst}")
        except Exception as e:
            print(f"Error extracting translations: {e}")

    # 4. Patch all _generatedTranslations.js files
    files = glob.glob('/opt/invenio/src/.venv/lib/python3.12/site-packages/**/_generatedTranslations.js', recursive=True) + glob.glob('/opt/invenio/var/instance/assets/**/_generatedTranslations.js', recursive=True)
    for f in files:
        with open(f, 'r') as fp:
            content = fp.read()
        if 'TRANSLATE_GA' not in content:
            lines = content.split('\n')
            last_import = -1
            for i, line in enumerate(lines):
                if line.startswith('import '):
                    last_import = i
            if last_import != -1:
                lines.insert(last_import + 1, 'import TRANSLATE_GA from "./ga/translations.json";')
            content = '\n'.join(lines)
            if 'export const translations = {' in content:
                content = content.replace(
                    'export const translations = {',
                    'export const translations = {\n  ga: { translation: TRANSLATE_GA },'
                )
            with open(f, 'w') as fp:
                fp.write(content)
            print(f"Patched _generatedTranslations.js: {f}")

if __name__ == '__main__':
    main()
