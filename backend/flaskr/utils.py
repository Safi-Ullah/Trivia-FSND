from models import Category, Question


PAGE_LIMIT = 10


def get_range(page):
    """
    Get page range.

    :param page:
    :return: start, end
    """
    page_index = page - 1
    start = page_index * PAGE_LIMIT
    end = start + PAGE_LIMIT
    return start, end


def get_questions_list(page=None, query=None, category_id=None):
    """
    Return list of questions.

    :param query:
    :param category_id:
    :return:
    """
    if query:
        questions = Question.query.filter(
            Question.question.ilike(f'%{query}%')
        ).all()
    elif category_id:
        questions = Question.query.order_by(Question.id).filter_by(category=category_id).all()
    else:
        questions = Question.query.order_by(Question.id).all()

    total_questions_count = len(questions)
    if page:
        start, end = get_range(page)
        questions = questions[start:end]

    return [question.format() for question in questions], total_questions_count
