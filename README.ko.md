# Citation Rigor Checker

[English](README.md) · **한국어**

**매번 긴 프롬프트를 작성하지 않고, 정해 둔 인용 검증 절차를 재사용하세요.**

참고문헌 점검, 주장과 출처의 대조, 근거 기록, 검토 범위 보고를 위한 지침을 묶은 [Agent Skill](https://agentskills.io/specification)입니다. 파일과 원하는 검토 범위를 알려 주면 저장된 지침을 불러와 세부 절차를 따르도록 합니다.

핵심 가치는 반복해서 프롬프트를 쓰는 부담을 줄이고, 여러 감사에 공통 절차를 적용할 수 있다는 점입니다. 근거 수준, 불확실성, 인용 위치 연결, 보고서 형식을 논문마다 다시 설명할 필요가 없습니다. 실제 모델의 지침 준수와 출력 품질은 달라질 수 있습니다.

**정확도 우위는 입증되지 않았습니다.** 공개된 개발 자료 비교에서는 과제와 라벨 정의를 명시한 기본 프롬프트와 동점이었습니다. 프롬프트 작성 부담 감소와 실제 작업에서의 절차 일관성도 사용자 연구로 측정한 결과는 아닙니다. [평가 결과와 한계](benchmarks/README.md)를 공개합니다.

빠른 **lite 보고서**, **심사자 수준의 full 감사**, 선택적 Python 서지 점검 도구를 제공합니다. 스크립트 없이 지침만으로도 사용할 수 있습니다.

[잡아낸 사례](examples/caught-issues.md) · [평가 결과](benchmarks/README.md) · [낮은 점수의 원인 분석](benchmarks/DIAGNOSIS.ko.md) · [스킬 본문](SKILL.md)

## 무엇을 확인하나요?

- **참고문헌이 식별 가능한 실제 출판물/프리프린트와 일치하는가?**와 **그 출처가 이 문장을 뒷받침하는가?**를 따로 판정합니다.
- 같은 논문을 여러 번 인용하거나 여러 출처를 함께 인용한 경우에도 각 인용 위치를 연결합니다.
- 방법론의 변경, 실험 결과의 과장, 데이터셋과 시뮬레이터의 혼동을 확인합니다.
- 참고문헌 전체에 서지 점검을 먼저 시도하고, 핵심 기여 → 차용한 방법/수식 → 비교 실험 → 배경 설명 순으로 의미 검증을 진행합니다.
- 근거 위치, 구체적인 문장 수정안, 아직 확인하지 못한 항목을 남깁니다.

PMLR의 높은 페이지 수, 본 학회 논문의 포스터 발표, 출판연도 차이, PDF 기호 추출 문제는 실제 출처와 대조합니다. 특이해 보인다는 이유만으로 오류로 판정하지 않습니다.

## 설치

GitHub의 **Code → Download ZIP**으로 내려받아 압축을 풀고, 폴더 이름을 `citation-rigor-checker`로 바꾼 뒤 아래 위치로 복사하세요. `SKILL.md`가 그 폴더 바로 아래에 있어야 합니다. 선택적 도구와 추가 지침을 사용하려면 `scripts/`, `references/`도 포함하고 `LICENSE`를 유지하세요.

### Codex

- 개인용: `~/.agents/skills/citation-rigor-checker/`
- 프로젝트용: `<project>/.agents/skills/citation-rigor-checker/`
- Windows 개인용: `%USERPROFILE%\.agents\skills\citation-rigor-checker\`

Codex CLI/IDE에서 `$citation-rigor-checker`로 호출하거나 `/skills`에서 선택하세요. 새로 설치한 스킬이 보이지 않으면 다시 시작하세요. [OpenAI 스킬 문서](https://learn.chatgpt.com/docs/build-skills)를 참고하세요.

### Claude Code

- 개인용: `~/.claude/skills/citation-rigor-checker/`
- 프로젝트용: `<project>/.claude/skills/citation-rigor-checker/`
- Windows 개인용: `%USERPROFILE%\.claude\skills\citation-rigor-checker\`

`/citation-rigor-checker`로 호출하세요. 검색·다시 불러오기·클라우드 세션 차이는 [Claude Code 스킬 문서](https://code.claude.com/docs/en/skills)를 참고하세요.

이 저장소는 로컬 설치용 독립 스킬입니다. 다른 Agent Skills 호스트에서는 해당 호스트의 설치 경로와 호출 방식을 따릅니다.

## 사용 예시

파일을 첨부하거나 에이전트가 읽을 수 있는 위치에 두세요. 아래는 Codex용 예시입니다. Claude Code에서는 첫 줄을 `/citation-rigor-checker`로 바꾸면 됩니다.

### 짧은 요청으로 시작하기

```text
$citation-rigor-checker
manuscript.pdf와 references.bib를 lite 모드로 확인하고 한국어로 보고해 줘.
```

세부 검증 절차는 스킬에서 불러옵니다. 필요하면 아래 예시처럼 예산, 검토 범위, 보고서 요구사항을 덧붙이세요.

### 참고문헌 빠른 점검

```text
$citation-rigor-checker
첨부한 references.bib를 lite 모드로 확인해 줘.
외부 요청 40회 이내에서 모든 항목의 실재 여부와 서지를 점검하고,
근거 링크와 미확인 항목을 보여 줘.
원고는 없으니 주장에 대한 의미 검증은 Not assessed로 표시해 줘.
한국어로 보고해 줘.
```

### 예산을 정한 심사자 수준 감사

```text
$citation-rigor-checker
manuscript.pdf와 references.bib를 full 모드로 감사해 줘.
모든 참고문헌과 인용 위치를 먼저 목록화하고 서지 점검을 전수 시도해 줘.
의미 검증은 핵심 기여, 차용한 방법/수식, 비교 실험 주장 순으로 진행해 줘.
외부 요청은 60회, 서로 다른 출처의 전문 열람은 10개 이내로 제한해 줘.
진행 상태를 저장하고 주요 문제에는 정확한 문장 수정안을 제안해 줘.
```

### 원 방법의 변형 확인

```text
$citation-rigor-checker
초안 3절을 첨부한 원 논문과 비교해 줘.
추정량과 가정을 바꾼 부분을 정확하게 설명했는지 확인하고,
원 논문의 기여와 우리가 변형한 부분을 구분해 줘.
```

### 오프라인 점검

```text
$citation-rigor-checker
네트워크 없이 제공한 발췌문만 검토해 줘.
인용 연결과 내부 일관성을 확인하고, 추가로 필요한 출처 구절을 알려 줘.
자료가 부족한 판단은 unresolved로 남겨 줘.
```

lite 보고서는 서지와 주장 근거를 별도 항목으로 보여 줍니다. full 보고서는 참고문헌 등록부, 인용 위치별 감사, 근거 목록, 심사자 관점 검토를 추가합니다. 두 방식 모두 실제 확인 범위를 명시합니다. [오류를 발견한 예시](examples/caught-issues.md)와 [공개 논문 일부 감사](examples/attention-audit.md)를 참고하세요.

## 선택적 서지 점검 도구

Python 3.10 이상과 표준 라이브러리만 사용합니다. 저장소 폴더에서 실행하세요.

```bash
# 고정된 공개 메타데이터로 오프라인 재실행
python scripts/bibliography.py benchmarks/references.bib --snapshot benchmarks/sources.json --out preflight.json

# 요청 한도를 정한 실시간 조회 및 응답 캐시
python scripts/bibliography.py references.bib --live --max-requests 40 --out preflight.json
```

문서화된 BibTeX 부분집합을 파싱하고 Crossref DOI와 arXiv 식별자를 조회하며 필드를 비교합니다. 식별자가 없는 제목 검색은 검토할 후보를 반환합니다. 일반적인 TeX 악센트, 이름의 particle, 부제를 처리하고 단일 신호의 불일치는 review로 보냅니다. 지원하지 않는 BibTeX 매크로/상속은 명시적으로 실패합니다. [도구 상세 설명](references/helper.md)을 참고하세요.

같은 입력과 고정된 메타데이터로 결정론적 비교를 재실행할 수 있습니다. 실시간 검색과 모델 판정은 달라질 수 있습니다. 지침만 사용하는 흐름에는 Python이 필요 없으며, 검색·원문 열람에는 호스트의 도구와 사용량 제한이 적용됩니다.

## 분야와 언어의 범위

[출처 안내](references/sources.md)에는 ML/CS 자료 외에도 국문 KCI/RISS/DBpia, 의생명 PubMed, 도서·학위논문 조회 경로가 있습니다. 자동 조회 도구가 지원하는 서비스는 **Crossref와 arXiv**입니다. 국문 출처 경로가 있다는 사실이 국문 논문 정확도의 실증 검증을 의미하지는 않습니다.

## 검증 현황

실제 GPflow BibTeX 9개와 별도로 확인한 학술 레코드를 바탕으로 한 서지 사례, 여섯 의미 상태를 포함한 발췌문 사례를 제공합니다. 기존 40개 복사·변형 자료는 도구 회귀 점검용으로 보존합니다.

첫 비교의 낮은 스킬 점수에는 표기 차이를 오류로 센 라벨과 잘못된 자료 부재 제어 항목이 영향을 줬습니다. 원본 결과는 보존하고, [케이스별 원인 분석](benchmarks/DIAGNOSIS.ko.md), [재비교 프로토콜](benchmarks/adjudicated-v2/PROTOCOL.md), [모든 실행과 점수](benchmarks/README.md)를 공개합니다. 평가 기준 변경과 스킬 수정 효과를 구분하기 위해 기본 프롬프트·기존 스킬·수정 스킬을 같은 조건에서 비교합니다.

**재비교 9회 완료:** 기본 프롬프트·기존 스킬·수정 스킬을 각각 3회 실행했습니다. 모델은 `gpt-6.1-sol`, 추론 수준은 medium이며 입력·라벨 정의·도구 사용 조건이 같습니다. 모호한 2개를 제외한 서지 18개에서 평균 macro-F1은 순서대로 **1.000 / 1.000 / 1.000**, 의미 15개에서는 **1.000 / 1.000 / 1.000**입니다. 모호한 항목까지 포함한 보조 점수도 공개했습니다. 이 개발 자료에서 스킬의 일반적 우월성을 입증하지는 못했으며 의미 자료의 천장 효과도 남아 있습니다.

평균 입력 토큰은 수정 스킬 **23,802개**, 기본 프롬프트 **19,005개**로 스킬이 약 **25% 더 사용**했습니다. 직접 입력할 문장은 줄어도 저장된 지침은 모델 문맥에 포함되므로 사용량과 비용이 늘어날 수 있습니다.

개별 기능 확인 자료로는 표기 차이를 다룬 합성 회귀 사례 6개(도구 수정 전 심각한 identity-conflict 표시 **5개 → 수정 후 0개**)와 공개 BibTeX의 실제 오타 `Variatinoally`/`Variationally`를 보존합니다. 일반적인 정확도를 입증하는 결과는 아닙니다. [회귀 결과](benchmarks/results/normalization-regression.json) · [입력과 발견 내용](examples/caught-issues.md).

```bash
python -m unittest discover -s tests -v
python benchmarks/check_real_world.py
python benchmarks/diagnose.py
python benchmarks/summarize.py --dataset adjudicated-v2 --directory benchmarks/comparison-v2 --include-old-skill
```

## 한계

- **출력 오류 가능성:** 모델이 오류를 놓치거나 정상 인용을 오탐하고, 출처를 잘못 읽거나 지침을 따르지 않을 수 있습니다. 문제가 없다는 보고서도 정확성·완전성·독창성·투고 적합성을 인증하지 않습니다. 검색 실패는 허구의 증거가 아닙니다.
- **근거와 접근성:** 유료 원문, 누락된 버전, 불완전한 서지, OCR, 호스트 도구가 검토 범위를 제한합니다. 도구의 서지 비교는 예비 결과이며 토큰 겹침이 저자의 신원을 인증하지는 않습니다. 원문의 관련 부분을 직접 읽거나 독립적인 학술 검토를 받는 절차를 대체하지 않습니다.
- **평가 범위:** 같은 세션에서 라벨링한 소규모 개발 자료이며 독립 판정은 없습니다. 의미 자료에는 천장 효과가 있고 모델 이름은 고정된 내부 버전이 아닌 별칭입니다. 전체 원고 검색, 다국어·다른 호스트에서의 정확도, 시간 절약, 실제 절차 일관성은 검증하지 않았습니다. 한글 이름 회귀 사례는 합성 표기 테스트입니다.
- **자원과 기밀성:** 긴 입력은 문맥·사용량 한도를 넘을 수 있고 스킬과 도구 사용에도 자원이 듭니다. 원고와 출처 자료를 선택한 서비스에 제공할 권한이 있는지 사용자가 확인해야 합니다. 기밀 자료를 공개 이슈나 허용되지 않은 외부 서비스에 올리지 마세요.

## 사용자 책임 및 면책

모든 결과는 사용자의 검토를 돕는 참고 자료입니다. **원문 확인, 제안된 수정의 검증, 최종 인용·투고·출판 결정의 책임은 사용자에게 있습니다.** 보고서만으로 허위 인용이나 연구 부정행위를 단정하지 마세요.

스킬·도구·예시·보고서는 **있는 그대로 제공**하며 정확성, 완전성, 특정 목적에 대한 적합성, 오류 없는 작동을 보증하지 않습니다. **관련 법률이 허용하는 최대 범위에서 저자와 저작권자는 이 프로젝트의 사용 또는 결과에 대한 의존으로 발생하는 청구·손해·기타 책임을 부담하지 않습니다.** 여기에는 인용 오류, 누락, 투고·출판 결과가 포함됩니다. 적용 조건은 [MIT LICENSE](LICENSE)와 [공식 라이선스 원문](https://opensource.org/license/mit)을 확인하세요. 법률상 배제할 수 없는 책임까지 배제한다는 뜻은 아닙니다.

## 기여

독립 판정을 거친 사례, 어려운 정상 인용, 다른 언어, 호스트 호환성 보고, 설정과 근거가 공개된 비교 실행을 환영합니다. 버그에는 최소한의 공개/합성 입력, 기대 결과와 실제 결과, 호스트·모델 또는 Python 버전을 포함해 주세요. 성능 향상을 주장하기 전 [평가 방법](benchmarks/README.md)을 확인해 주세요.

## 라이선스

[MIT](LICENSE)입니다. 이 저장소의 자료를 재사용할 때 저작권·허가 문구를 유지하세요. 인용한 논문·데이터셋·원고의 권리는 각 원 저작물의 조건을 따릅니다.
