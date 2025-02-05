def parse_keywords(comment, keyword):
    for line in comment.split('\n'):
        if keyword in line:
            line = line.replace('#', ' ').strip()
            return line.split(keyword)[-1].strip()