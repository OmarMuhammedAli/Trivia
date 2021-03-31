QUESTIONS_PER_PAGE = 10


def format_category_list(categories):
    cats = dict()
    for category in categories:
        cats[category.id] = category.type

    return cats


def paginate_questions(request, questions):
    """
    A helper method to return questions paginated
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    current_questions = [question.format()
                         for question in questions][start:end]

    return current_questions