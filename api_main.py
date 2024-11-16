from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import math

app = FastAPI()

class PersonInfo(BaseModel):
    full_name: str
    birth_date: str

class TwoPeopleCompatibilityRequest(BaseModel):
    person1: PersonInfo
    person2: PersonInfo

class DepartmentCompatibilityRequest(BaseModel):
    people: List[PersonInfo]

class CompatibilityResult(BaseModel):
    total_score: int
    compatibility_level: str
    explanations: Dict[str, List[str]]

class GroupCompatibilityResult(BaseModel):
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
            explanation.append(f"- Стихия {element} несбалансирована: {elements1[element]}% у одного, {elements2[element]}% у другого.")
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
            explanation.append(f"- Различия в стратегии {strategy} могут вызывать недопонимание (у одного {behaviors1[strategy]}%, у другого {behaviors2[strategy]}%).")
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

async def get_mock_data(person: PersonInfo):
    elements = {"Огонь": 30.0, "Земля": 20.0, "Воздух": 30.0, "Вода": 20.0}
    behaviors = {"Кардинальность": 33.3, "Фиксированность": 33.3, "Мутабельность": 33.4}
    astrology = {
        "Солнце": "Овен",
        "Луна": "Телец",
        "Венера": "Близнецы",
        "Марс": "Рак",
        "Юпитер": "Лев",
        "Сатурн": "Дева"
    }
    return elements, behaviors, astrology

async def calculate_group_compatibility(people_data: List[Dict]):
    n = len(people_data)
    results = []
    for i in range(n):
        total_score = 0
        for j in range(n):
            if i != j:
                compatibility = await calculate_compatibility(
                    people_data[i]['elements'], people_data[j]['elements'],
                    people_data[i]['behaviors'], people_data[j]['behaviors'],
                    people_data[i]['astrology'], people_data[j]['astrology']
                )
                total_score += compatibility.total_score
        results.append(GroupCompatibilityResult(
            full_name=people_data[i]['person'].full_name,
            total_score=total_score,
            recommendation="Рекомендация пока не реализована."
        ))
    return results

@app.post("/api/cosmostat/two-people")
async def get_compatibility_for_two(request: TwoPeopleCompatibilityRequest):
    try:
        elements1, behaviors1, astrology1 = await get_mock_data(request.person1)
        elements2, behaviors2, astrology2 = await get_mock_data(request.person2)
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
            elements, behaviors, astrology = await get_mock_data(person)
            people_data.append({
                'person': person,
                'elements': elements,
                'behaviors': behaviors,
                'astrology': astrology
            })
        results = await calculate_group_compatibility(people_data)
        return {
            "isSuccess": True,
            "errorMessage": None,
            "errorCode": 0,
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
