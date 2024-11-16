from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Tuple
import requests
import random
from dataclasses import dataclass

app = FastAPI()

class PersonInfo(BaseModel):
    full_name: str
    birth_date: str

class TwoPeopleCompatibilityRequest(BaseModel):
    person1: PersonInfo
    person2: PersonInfo

class DepartmentCompatibilityRequest(BaseModel):
    people: List[PersonInfo]

@dataclass
class CompatibilityResult:
    total_score: int
    compatibility_level: str
    explanations: Dict[str, List[str]]

@dataclass
class GroupCompatibilityResult:
    full_name: str
    total_score: int
    recommendation: str

async def analyze_elements(elements1: Dict[str, float], elements2: Dict[str, float]):
    score = 0
    explanation = []
    for element in ["Огонь", "Земля", "Воздух", "Вода"]:
        if elements1[element] > 40 and elements2[element] > 40:
            score -= 2
            explanation.append(f"- Обе стороны имеют доминирующую стихию {element}, это может привести к однотипному подходу и конфликтам.")
        elif abs(elements1[element] - elements2[element]) < 20:
            score += 2
            explanation.append(f"+ Стихия {element} сбалансирована между людьми, что способствует гармонии.")
        else:
            explanation.append(f"- Стихия {element} несбалансирована: {elements1[element]:.1f}% у одного, {elements2[element]:.1f}% у другого.")
    dominant_elements1 = sum(1 for v in elements1.values() if v > 40)
    dominant_elements2 = sum(1 for v in elements2.values() if v > 40)
    if dominant_elements1 == 0 and dominant_elements2 == 0:
        score += 3
        explanation.append("+ У обоих нет доминирующей стихии, что способствует гибкости и адаптивности.")
    elif dominant_elements1 > 1 or dominant_elements2 > 1:
        score -= 3
        explanation.append("- У одного из участников доминирует несколько стихий, что может усложнить взаимодействие.")
    return score, explanation

async def analyze_behaviors(behaviors1: Dict[str, float], behaviors2: Dict[str, float]):
    score = 0
    explanation = []
    for strategy in ["Кардинальность", "Фиксированность", "Мутабельность"]:
        if behaviors1[strategy] > 40 and behaviors2[strategy] > 40:
            score -= 2
            explanation.append(f"- Оба имеют доминирующую стратегию {strategy}, что может привести к столкновению интересов.")
        elif abs(behaviors1[strategy] - behaviors2[strategy]) < 20:
            score += 3
            explanation.append(f"+ Стратегия {strategy} уравновешена между участниками, это улучшает совместимость.")
        else:
            explanation.append(f"- Различия в стратегии {strategy} могут вызывать недопонимание (у одного {behaviors1[strategy]:.1f}%, у другого {behaviors2[strategy]:.1f}%).")
    dominant_strategies1 = sum(1 for v in behaviors1.values() if v > 40)
    dominant_strategies2 = sum(1 for v in behaviors2.values() if v > 40)
    if dominant_strategies1 == 1 and dominant_strategies2 == 1:
        score += 2
        explanation.append("+ У обоих участников доминирует только одна стратегия, что способствует сосредоточенности.")
    elif dominant_strategies1 > 1 or dominant_strategies2 > 1:
        score -= 2
        explanation.append("- У одного из участников слишком много доминирующих стратегий, что может усложнить взаимодействие.")
    return score, explanation

async def analyze_astrology(astrology1: Dict[str, str], astrology2: Dict[str, str]):
    score = 0
    explanation = []
    if astrology1["Солнце"] == astrology2["Луна"] or astrology2["Солнце"] == astrology1["Луна"]:
        score += 3
        explanation.append("+ Солнце и Луна гармонируют, это улучшает эмоциональную совместимость.")
    else:
        score -= 1
        explanation.append("- Солнце и Луна не гармонируют, возможны эмоциональные разногласия.")
    if astrology1["Венера"] == astrology2["Марс"] or astrology2["Венера"] == astrology1["Марс"]:
        score += 2
        explanation.append("+ Венера и Марс гармонируют, это улучшает социальные и профессиональные отношения.")
    else:
        score -= 2
        explanation.append("- Венера и Марс не гармонируют, возможны трудности в личных и рабочих взаимодействиях.")
    if astrology1["Солнце"][:1] == astrology2["Солнце"][:1]:
        score += 2
        explanation.append("+ Солнце в знаках одной стихии, это улучшает понимание и общие цели.")
    else:
        explanation.append("- Солнце в разных стихиях, возможны разногласия в подходе к задачам.")
    return score, explanation

async def calculate_compatibility(elements1, elements2, behaviors1, behaviors2, astrology1, astrology2):
    element_score, element_explanation = await analyze_elements(elements1, elements2)
    behavior_score, behavior_explanation = await analyze_behaviors(behaviors1, behaviors2)
    astrology_score, astrology_explanation = await analyze_astrology(astrology1, astrology2)
    total_score = element_score + behavior_score + astrology_score
    if total_score >= 8:
        level = "Высокая совместимость"
    elif 4 <= total_score < 8:
        level = "Средняя совместимость"
    else:
        level = "Низкая совместимость"
    explanations = {
        "Стихии": element_explanation,
        "Стратегии поведения": behavior_explanation,
        "Астрология": astrology_explanation,
    }
    return CompatibilityResult(total_score=total_score, compatibility_level=level, explanations=explanations)

def map_planet_to_sign(sign_index):
    signs = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
    if 0 <= sign_index < len(signs):
        return signs[sign_index]
    else:
        return "Неизвестно"

async def get_real_data(person: PersonInfo):
    url = "https://www.lifexpert.ru/jui/rpc/"
    headers = {
        "Content-Type": "application/json"
    }
    date_str = person.birth_date
    payload = [
        {
            "jsonrpc": "2.0",
            "id": 53,
            "method": "datetime_calcs.astro_frame",
            "params": {
                "date": date_str,
                "coord": {
                    "lat": 59.9503,
                    "lng": 30.3903,
                    "country": "RU",
                    "verbose": "Центральный р-н, Санкт-Петербург"
                },
                "options": {
                    "houses_system": "K",
                    "use_aspect_node": False,
                    "use_aspect_lilith": False
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 54,
            "method": "datetime_calcs.destinywill",
            "params": {
                "date": date_str
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 55,
            "method": "datetime_calcs.pifagor_frame",
            "params": {
                "date": date_str,
                "death_date": None,
                "fio": [],
                "use_1999": False
            }
        }
    ]
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if not data or 'result' not in data[0]:
            raise Exception(f"Invalid data received for {person.full_name}")
        astro_frame = data[0]['result']
        elements_data = astro_frame['elements']
        elements = {
            "Огонь": elements_data['elements']['fire'] * 100,
            "Земля": elements_data['elements']['earth'] * 100,
            "Воздух": elements_data['elements']['air'] * 100,
            "Вода": elements_data['elements']['water'] * 100
        }
        behaviors = {
            "Кардинальность": elements_data['strategy']['cardinal'] * 100,
            "Фиксированность": elements_data['strategy']['constant'] * 100,
            "Мутабельность": elements_data['strategy']['mutable'] * 100
        }
        planets = astro_frame['planets']
        astrology = {}
        for planet_name in ["sun", "moon", "venus", "mars", "jupiter", "saturn"]:
            if planet_name in planets and len(planets[planet_name]) > 1:
                sign_index = planets[planet_name][1]
                astrology_name = {
                    "sun": "Солнце",
                    "moon": "Луна",
                    "venus": "Венера",
                    "mars": "Марс",
                    "jupiter": "Юпитер",
                    "saturn": "Сатурн"
                }[planet_name]
                astrology[astrology_name] = map_planet_to_sign(sign_index)
            else:
                astrology[astrology_name] = "Неизвестно"
        return elements, behaviors, astrology
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

MOTIVATIONAL_RECOMMENDATIONS = [
    "Проведите индивидуальную беседу для понимания текущих трудностей сотрудника.",
    "Организуйте тренинг по развитию необходимых навыков.",
    "Предложите менторскую поддержку от опытного коллеги.",
    "Проверьте нагрузку на сотрудника и при необходимости скорректируйте её.",
    "Предоставьте возможность участия в проектах, соответствующих интересам сотрудника.",
    "Обеспечьте регулярную обратную связь и поощрение за достижения.",
    "Проведите оценку условий труда и внесите необходимые улучшения.",
    "Предложите гибкий график работы для повышения комфорта.",
    "Организуйте тимбилдинг для улучшения взаимодействия в коллективе.",
    "Предложите возможность дополнительного обучения или повышения квалификации.",
    "Разработайте план карьерного роста совместно с сотрудником.",
    "Проведите анкетирование для выявления потребностей и пожеланий сотрудника.",
    "Обеспечьте доступ к ресурсам для управления стрессом и эмоциональным выгоранием.",
    "Улучшите коммуникацию внутри команды для повышения прозрачности процессов.",
    "Предложите бонусы или иные формы мотивации за повышение эффективности.",
    "Организуйте семинары по тайм-менеджменту и эффективному планированию.",
    "Обеспечьте комфортные условия для работы, включая эргономичное оборудование.",
    "Проведите анализ рабочей нагрузки и перераспределите задачи при необходимости.",
    "Предложите участие в корпоративных инициативах для повышения вовлеченности.",
    "Создайте благоприятную атмосферу для открытого выражения идей и предложений.",
    "Проведите анализ сильных и слабых сторон сотрудника для целенаправленного развития.",
    "Организуйте воркшопы по развитию лидерских качеств.",
    "Предложите участие в программах обмена опытом с другими отделами.",
    "Устройте дни открытых дверей для обсуждения карьерных возможностей.",
    "Предоставьте доступ к онлайн-курсам и образовательным платформам.",
    "Разработайте систему признания достижений сотрудников на регулярной основе.",
    "Создайте программы поощрения за инновационные идеи и инициативу.",
    "Организуйте мероприятия для улучшения здоровья и благополучия сотрудников.",
    "Предложите бесплатные обеды или перерывы для отдыха и общения.",
    "Внедрите программы по улучшению баланса между работой и личной жизнью.",
    "Предоставьте возможность удаленной работы или гибких графиков.",
    "Создайте менторские программы для поддержки профессионального роста.",
    "Проведите семинары по развитию эмоционального интеллекта.",
    "Организуйте конкурсы с призами для стимулирования креативности.",
    "Обеспечьте прозрачность в оценке и продвижении по карьерной лестнице.",
    "Предложите возможности для участия в благотворительных проектах.",
    "Разработайте планы индивидуального развития для каждого сотрудника.",
    "Устройте вечеринки или корпоративные мероприятия для укрепления команды.",
    "Внедрите системы поощрения за долгосрочное сотрудничество."
]

def generate_recommendation(score: int, average_score: float) -> str:
    """
    Генерирует рекомендацию на основе сравнения балла сотрудника со средним баллом группы.

    :param score: Балл сотрудника
    :param average_score: Средний балл группы
    :return: Строка с рекомендацией
    """
    if score < average_score:
        recommendation = random.choice(MOTIVATIONAL_RECOMMENDATIONS)
        return f"Рекомендация: {recommendation}"
    else:
        return "Рекомендация: Сотрудник показывает хороший уровень. Продолжайте поддерживать текущую мотивацию и развитие."



async def calculate_group_compatibility(people_data: List[Dict]) -> Tuple[List[GroupCompatibilityResult], List[List[int]]]:
    """
    Рассчитывает совместимость группы сотрудников и возвращает результаты с рекомендациями и матрицу совместимости.

    :param people_data: Список данных о сотрудниках.
    :return: Кортеж из списка результатов и матрицы совместимости.
    """
    n = len(people_data)
    results = []
    compatibility_matrix = [[0 for _ in range(n)] for _ in range(n)]

    total_sum_score = 0
    for i in range(n):
        for j in range(i + 1, n):
            compatibility = await calculate_compatibility(
                people_data[i]['elements'], people_data[j]['elements'],
                people_data[i]['behaviors'], people_data[j]['behaviors'],
                people_data[i]['astrology'], people_data[j]['astrology']
            )
            compatibility_score = compatibility.total_score
            compatibility_matrix[i][j] = compatibility_score
            compatibility_matrix[j][i] = compatibility_score
            total_sum_score += compatibility_score

    for i in range(n):
        total_score = sum(compatibility_matrix[i])
        recommendation = generate_recommendation(total_score, total_sum_score)
        results.append(GroupCompatibilityResult(
            full_name=people_data[i]['person'].full_name,
            total_score=total_score,
            recommendation=recommendation
        ))

    return results, compatibility_matrix


@app.post("/api/cosmostat/two-people")
async def get_compatibility_for_two(request: TwoPeopleCompatibilityRequest):
    try:
        elements1, behaviors1, astrology1 = await get_real_data(request.person1)
        elements2, behaviors2, astrology2 = await get_real_data(request.person2)
        result = await calculate_compatibility(elements1, elements2, behaviors1, behaviors2, astrology1, astrology2)
        return {
            "isSuccess": True,
            "errorMessage": None,
            "errorCode": 0,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/cosmostat/department")
async def get_compatibility_for_department(request: DepartmentCompatibilityRequest):
    try:
        people_data = []
        for person in request.people:
            elements, behaviors, astrology = await get_real_data(person)
            people_data.append({
                'person': person,
                'elements': elements,
                'behaviors': behaviors,
                'astrology': astrology
            })
        results, compatibility_matrix = await calculate_group_compatibility(people_data)
        return {
            "isSuccess": True,
            "errorMessage": None,
            "errorCode": 0,
            "data": {
            "results": results, 
            "compatibility_matrix": compatibility_matrix
            }
                
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
