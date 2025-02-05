def parse_keywords(comment, keyword):
    for line in comment.split('\n'):
        if keyword in line:
            return line.split(':')[-1].strip()