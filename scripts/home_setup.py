"""Configure the official Home on Fire 1.5.2 through its visible Android UI."""
import re
import time
import xml.etree.ElementTree as ET

PACKAGE = 'io.github.toolicious.homeonfire'
TARGET = 'dev.plume.salah'


def bounds(node):
    values = list(map(int, re.findall(r'\d+', node.get('bounds', ''))))
    if len(values) != 4 or values[2] <= values[0] or values[3] <= values[1]:
        raise RuntimeError('Element hors ecran ou sans dimensions')
    return values


class Screen:
    def __init__(self, adb, logs):
        self.adb, self.logs = adb, logs
        self.counter = 0

    def read(self):
        # Never click another app if launch or a remote key has changed the foreground.
        if PACKAGE + '/' not in self.adb.resumed():
            raise RuntimeError('Home on Fire a quitte le premier plan. Relancer la configuration sans toucher la telecommande.')
        self.adb.run('shell', 'uiautomator', 'dump', '/sdcard/plume-chill-setup.xml')
        xml = self.adb.run('exec-out', 'cat', '/sdcard/plume-chill-setup.xml')
        tree = ET.fromstring(xml)
        if not any(n.get('package') == PACKAGE for n in tree.iter('node')):
            raise RuntimeError('Ecran Home on Fire non reconnu : intervention sur la TV necessaire.')
        self.counter += 1
        (self.logs / ('home-%02d.xml' % self.counter)).write_text(xml, encoding='utf-8')
        return tree

    def tap(self, tree, node):
        parents = {child: parent for parent in tree.iter() for child in parent}
        while node.get('clickable') != 'true' and node in parents:
            node = parents[node]
        if node.get('clickable') != 'true' or node.get('enabled') != 'true':
            raise RuntimeError('Controle Home on Fire non activable')
        left, top, right, bottom = bounds(node)
        self.adb.run('shell', 'input', 'tap', str((left + right) // 2), str((top + bottom) // 2))
        time.sleep(.5)

    def enable(self, fragment):
        tree = self.read()
        label = next((n for n in tree.iter('node') if fragment in n.get('text', '')), None)
        if label is None:
            raise RuntimeError('Option absente : ' + fragment)
        parents = {child: parent for parent in tree.iter() for child in parent}
        container = label
        while container is not None:
            switches = [n for n in container.iter('node') if n.get('class') == 'android.widget.Switch']
            if switches:
                if len(switches) != 1:
                    raise RuntimeError('Option ambigue : ' + fragment)
                switch = switches[0]
                if switch.get('checked') != 'true':
                    self.tap(tree, switch)
                    check = self.read()
                    # The setting must be confirmed in a fresh dump, not inferred from the tap.
                    confirm_label = next(n for n in check.iter('node') if fragment in n.get('text', ''))
                    cp = {c: p for p in check.iter() for c in p}
                    box = confirm_label
                    while not any(n.get('class') == 'android.widget.Switch' for n in box.iter('node')):
                        box = cp[box]
                    if not any(n.get('class') == 'android.widget.Switch' and n.get('checked') == 'true' for n in box.iter('node')):
                        raise RuntimeError('Activation non confirmee : ' + fragment)
                return
            container = parents.get(container)
        raise RuntimeError('Interrupteur introuvable : ' + fragment)


def configure(adb, logs):
    adb.run('shell', 'pm', 'grant', PACKAGE, 'android.permission.WRITE_SECURE_SETTINGS')
    adb.run('shell', 'input', 'keyevent', 'KEYCODE_WAKEUP')
    adb.run('shell', 'am', 'start', '-W', '-n', PACKAGE + '/.MainActivity')
    for _ in range(20):
        if PACKAGE + '/' in adb.resumed():
            break
        time.sleep(.3)
    screen = Screen(adb, logs)
    tree = screen.read()
    selected = next((n for n in tree.iter('node') if 'Plume TV Chill (' + TARGET + ')' in n.get('text', '')), None)
    if selected is None:
        chip = next((n for n in tree.iter('node') if n.get('text', '').startswith('Choose target app')
                     or re.search(r'\([a-zA-Z0-9_.]+\)', n.get('text', '')) and n.get('text', '').endswith(')')), None)
        if chip is None:
            raise RuntimeError('Selecteur de cible Home on Fire introuvable')
        screen.tap(tree, chip)
        for _ in range(14):
            tree = screen.read()
            target = next((n for n in tree.iter('node') if n.get('text') == TARGET), None)
            if target is not None:
                screen.tap(tree, target)
                break
            nodes = [bounds(n) for n in tree.iter('node') if n.get('bounds') and n.get('bounds') != '[0,0][0,0]']
            width = max(b[2] for b in nodes); height = max(b[3] for b in nodes)
            adb.run('shell', 'input', 'swipe', str(width // 2), str(height * 4 // 5), str(width // 2), str(height // 4), '450')
            time.sleep(.3)
        else:
            raise RuntimeError('Plume TV Chill absent du selecteur')
    tree = screen.read()
    if not any('Plume TV Chill (' + TARGET + ')' in n.get('text', '') for n in tree.iter('node')):
        raise RuntimeError('Cible Home non confirmee')
    screen.enable('Accessibility service')
    screen.enable('Home button')
    screen.enable('Launch on boot')
    if int(adb.run('shell', 'getprop', 'ro.build.version.sdk')) <= 28:
        tree = screen.read()
        animation = next((n for n in tree.iter('node') if n.get('text') == 'Animation'), None)
        if animation is not None:
            screen.tap(tree, animation)
        tree = screen.read()
        if not any(n.get('text') == 'Black screen' for n in tree.iter('node')):
            raise RuntimeError('Ecran noir de transition non confirme')
    services = adb.run('shell', 'settings', 'get', 'secure', 'enabled_accessibility_services')
    if PACKAGE + '/' not in services:
        raise RuntimeError('Service Home on Fire non actif')
    print('Home on Fire : cible Plume TV Chill, accessibilite et demarrage actives.', flush=True)
