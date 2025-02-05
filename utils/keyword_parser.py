def parse_keywords(comment, keyword):
    for line in comment.split('\n'):
        if keyword in line:
            line.replace('#', '')
            return line.split(keyword)[-1].strip()