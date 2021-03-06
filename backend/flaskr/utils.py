QUESTIONS_PER_PAGE = 10  # Number of questions to be used in pagination.


def format_category_list(categories):
    """
    @param: categories retrieved from the db and sent from the controller.
    returns: a category formatted to abide by the UI requirements.
    """
    cats = dict()
    for category in categories:
        cats[category.id] = category.type

    return cats


def paginate_questions(request, questions):
    """
    A helper method to return questions paginated.
    @param: request sent from the front-end.
    @param: questions retrieved from the db and sent from the controller.
    returns: questions paginated for the current page.
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    current_questions = [question.format()
                         for question in questions][start:end]

    return current_questions
