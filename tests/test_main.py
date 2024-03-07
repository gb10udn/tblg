import sys
sys.path.append('./')

import main


def test_obtain_ref_path():
    result = main.obtain_ref_path('ui.js')
    assert result == './ref/ui.js'

    result = main.obtain_ref_path(file_name='ui.js', base_dir='./piyopiyo')
    assert result == './piyopiyo/ui.js'