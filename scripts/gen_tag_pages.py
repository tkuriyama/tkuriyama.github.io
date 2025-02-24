import os
from typing import List


################################################################################


def main():
    """Generaet tag pages."""
    fnames = walk_dir('../')
    tags = set(tag for fname in fnames for tag in get_tags(fname))
    for tag in tags:
        gen_tag_page('../tag', tag)

    print(f'Generated pages for {tags}')
    return tags


def walk_dir(root_dir):
    """Walk all subdirectories."""
    return [os.path.join(dirpath, fname)
            for dirpath, _, fnames in os.walk(root_dir)
            for fname in fnames
            if '_posts' in dirpath and '.md' in fname]


################################################################################
# Markdown Parsing and Page Generation


def get_tags(fname: str) -> List[str]:
    """Extract tags from MD, expecting oneline `tags: tag1 tag2...`"""
    with open(fname, 'r') as f:
        lines = [line for line in f.readlines() if line[:5] == 'tags:']

    if len(lines) != 1:
        print(f'File {fname} has unexpected layout, found {lines}')
        tags = []
    else:
        tags = lines[0].split('tags:')[1].strip().split(' ')

    return tags


def gen_tag_page(root_dir, tag):
    """Generate tag page."""
    content = (
        '---\n'
        'layout: tags.html\n'
        f'title: "Tag: {tag}"\n'
        f'tag: {tag}\n'
        '---\n'
    )
    with open(os.path.join(root_dir, f'{tag}.md'), 'w') as f:
        f.write(content)


################################################################################


if __name__ == '__main__':
    main()
