"""
Copyright (C) 2022 Abraham George Smith

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import os
import shutil

from os.path import join

def fix_app():
    """
    Unfortunately pyInstaller is no longer capable of building on it's own.

    It may be that I upgraded library versions to ones which are no longer
    supported i.e scikit-image.
    
    We will need to copy accross some dependencies to get it working again.
    """
    env_dir = './env'
    assert os.path.isdir(env_dir), f'Could not find env folder {env_dir}'
    site_packages_dir = os.path.join(env_dir, 'Lib', 'site-packages')
    build_dir = './target/DicomOutliner'

    # Copy missing orb files
    skimage_dir = join(site_packages_dir, 'skimage')
    orbpy_src = join(skimage_dir, 'feature/_orb_descriptor_positions.py')
    orbpy_target = join(build_dir, 'skimage/feature/_orb_descriptor_positions.py')
    print('copying', orbpy_target)
    shutil.copyfile(orbpy_src, orbpy_target)

    # copy missing orb plugin file
    orbtxt_src = join(skimage_dir, 'feature/orb_descriptor_positions.txt')
    orbtxt_target = join(build_dir, 'skimage/io/_plugins/orb_descriptor_positions.txt')
    print('copying', orbtxt_target)
    shutil.copyfile(orbtxt_src, orbtxt_target)

    # Copy missing tiffile plugin
    tif_src = join(skimage_dir, 'io/_plugins/tifffile_plugin.py')
    tif_target = join(build_dir, 'skimage/io/_plugins/tifffile_plugin.py')
    print('copying', tif_target)
    shutil.copyfile(tif_src, tif_target)

    src = join(site_packages_dir, 'pydicom')
    target = join(build_dir, 'pydicom')
    print('copying', src, 'to', target)
    shutil.copytree(src, target)


    # copy pydicom

    for dir_name in ['filters', 'metrics', 'segmentation', 'restoration']:
        if not os.path.isdir(os.path.join(build_dir, 'skimage', dir_name)):
            os.makedirs(os.path.join(build_dir, 'skimage', dir_name))
        for f in os.listdir(os.path.join(skimage_dir, dir_name)):
            src = join(skimage_dir, dir_name, f)
            target = join(build_dir, 'skimage', dir_name, f)
            if not os.path.isfile(target) and not os.path.isdir(src):
                print('copying', target)
                shutil.copyfile(src, target)

if __name__ == '__main__':
    fix_app()

