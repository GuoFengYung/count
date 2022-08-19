import argparse
import json
from dataclasses import dataclass
from typing import List, Optional, Tuple
import os
from pathlib import Path
from tqdm import tqdm
from lib.logger import Logger


@dataclass
class Annotation:
    @dataclass
    class Size:
        width: int
        height: int
        depth: int

    @dataclass
    class Object:
        @dataclass
        class BBox:
            left: int
            top: int
            right: int
            bottom: int

        @dataclass
        class Mask:
            color: int

        name: str
        difficult: bool
        bbox: BBox
        mask: Optional[Mask]
        polygon: List[Tuple[float, float]]

    filename: str
    size: Size
    objects: List[Object]


def read_src_annotation(path_to_annotation_json: str) -> Annotation:
    with open(path_to_annotation_json, 'r', errors='ignore') as f:
        annotation_dict = json.load(f)
    annotation = Annotation(
        filename=annotation_dict['imagePath'],
        size=Annotation.Size(
            width=annotation_dict['imageWidth'],
            height=annotation_dict['imageHeight'],
            depth=3
        ),
        objects=[Annotation.Object(
            name=shape['label'],
            difficult=shape['flags']['difficult'] if 'difficult' in shape['flags'] else False,
            bbox=Annotation.Object.BBox(
                left=int(min(p[0] for p in shape['points'])),
                top=int(min(p[1] for p in shape['points'])),
                right=int(max(p[0] for p in shape['points'])),
                bottom=int(max(p[1] for p in shape['points']))
            ),
            mask=None if shape['shape_type'] != 'polygon' else Annotation.Object.Mask(color=i + 1),
            # ignore background color
            polygon=None if shape['shape_type'] != 'polygon' else [tuple(p) for p in shape['points']]
        ) for i, shape in enumerate(annotation_dict['shapes'])]
    )
    return annotation


def convert(path_to_src_dir: str, path_to_log: str):

    path_to_src_annotation_jsons = sorted([path.as_posix() for path in Path(path_to_src_dir).rglob(f'*.json')])
    print('Found {:d} JSON files'.format(len(path_to_src_annotation_jsons)))
    bbox = []
    for path_to_src_annotation_json in tqdm(path_to_src_annotation_jsons):

        annotation = read_src_annotation(path_to_src_annotation_json)
        for obj in annotation.objects:
            bbox.append(obj.bbox)
    print('Found {:d} bbox'.format(len(bbox)))

    logger = Logger.build(name=os.path.basename(os.getcwd()),
                          path_to_log_file=os.path.join(path_to_log + os.path.sep + 'count.log'))
    logger.i('Found {:d} JSON files'.format(len(path_to_src_annotation_jsons)))
    logger.i('Found {:d} bbox'.format(len(bbox)))


if __name__ == '__main__':
    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--src_dir', type=str, required=True, help='path to source directory')
        parser.add_argument('-o', '--src_log', type=str, required=True, help='path to log')

        args = parser.parse_args()
        path_to_src_dir = args.src_dir
        path_to_log_dir = args.src_log
        assert os.path.isdir(path_to_src_dir)

        path_to_src_dir = args.src_dir
        convert(path_to_src_dir, path_to_log_dir)


    main()
