import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class EnhancedJSONGenerator:
    """
    교육 문서를 고도화된 JSON으로 변환
    - 계층 구조 (document > section > table > row)
    - structured_data 자동 추출
    - queryable_facts 생성
    - Parent-Child 관계 설정
    """

    def __init__(self):
        self.document_id_counter = 0
        self.section_id_counter = 0
        self.table_id_counter = 0

    def generate_from_markdown(
        self,
        markdown_text: str,
        metadata: dict
    ) -> dict:
        """
        마크다운 텍스트를 Enhanced JSON으로 변환

        Args:
            markdown_text: PDFTableParser로 파싱된 마크다운
            metadata: {school_code, school_name, year, grade, subject, ...}

        Returns:
            Enhanced JSON 구조
        """
        self.section_id_counter = 0
        self.table_id_counter = 0

        # 1. 페이지별로 분할
        pages = self._split_by_pages(markdown_text)

        # 2. 각 페이지를 섹션으로 변환
        sections = []
        for page_num, page_content in enumerate(pages, 1):
            page_sections = self._parse_page_to_sections(page_content, page_num)
            sections.extend(page_sections)

        # 3. 문서 ID 생성
        doc_id = self._generate_document_id(metadata)

        # 4. 최종 JSON 구조
        enhanced_json = {
            "document_metadata": {
                "document_id": doc_id,
                **metadata,
                "extraction_method": "pdfplumber",
                "extraction_timestamp": datetime.now().isoformat(),
                "page_count": len(pages),
                "section_count": len(sections),
                "table_count": sum(len(s["tables"]) for s in sections)
            },
            "sections": sections,
            "rag_optimization": self._generate_rag_metadata(sections, doc_id)
        }

        return enhanced_json

    def _split_by_pages(self, text: str) -> List[str]:
        """## Page N 기준으로 페이지 분할"""
        pages = []
        current_page = []

        for line in text.split('\n'):
            if line.startswith('## Page '):
                if current_page:
                    pages.append('\n'.join(current_page))
                current_page = [line]
            else:
                current_page.append(line)

        if current_page:
            pages.append('\n'.join(current_page))

        return pages

    def _parse_page_to_sections(self, page_text: str, page_num: int) -> List[dict]:
        """페이지를 섹션으로 분할"""
        sections = []
        lines = page_text.split('\n')

        current_section_title = "문서 정보"
        current_content = []
        in_table = False
        current_table = []

        for line in lines:
            # 섹션 헤더 감지 (숫자로 시작하는 제목)
            if re.match(r'^\d+\.\s+', line):
                # 이전 섹션 저장
                if current_content or current_table:
                    section = self._build_section(
                        current_section_title,
                        current_content,
                        current_table,
                        page_num
                    )
                    if section:
                        sections.append(section)

                # 새 섹션 시작
                current_section_title = line
                current_content = []
                current_table = []
                in_table = False

            # 테이블 시작 감지
            elif line.startswith('| ') and '|' in line:
                in_table = True
                current_table.append(line)

            # 테이블 종료 감지
            elif in_table and not line.startswith('| '):
                in_table = False
                current_content.append('\n'.join(current_table))
                current_table = []
                if line.strip():
                    current_content.append(line)

            # 일반 텍스트
            else:
                if in_table:
                    current_table.append(line)
                else:
                    current_content.append(line)

        # 마지막 섹션 저장
        if current_content or current_table:
            section = self._build_section(
                current_section_title,
                current_content,
                current_table,
                page_num
            )
            if section:
                sections.append(section)

        return sections

    def _build_section(
        self,
        title: str,
        content_lines: List[str],
        table_lines: List[str],
        page_num: int
    ) -> Optional[dict]:
        """섹션 객체 생성"""
        section_id = f"sec_{self.section_id_counter:03d}"
        self.section_id_counter += 1

        # 내용 결합
        narrative_content = '\n'.join([
            line for line in content_lines
            if not line.startswith('| ')
        ]).strip()

        # 테이블 추출
        tables = []

        # content_lines에 포함된 테이블 추출
        for content in content_lines:
            if content.startswith('| ') and content.count('|') > 2:
                table_obj = self._parse_markdown_table(content, section_id)
                if table_obj:
                    tables.append(table_obj)

        # table_lines 처리
        if table_lines:
            table_text = '\n'.join(table_lines)
            table_obj = self._parse_markdown_table(table_text, section_id)
            if table_obj:
                tables.append(table_obj)

        # 섹션 타입 분류
        section_type = "narrative"
        if len(tables) > 0 and len(narrative_content) < 100:
            section_type = "table_dominant"
        elif len(tables) > 0:
            section_type = "mixed"

        return {
            "section_id": section_id,
            "section_title": title.strip(),
            "section_type": section_type,
            "page_number": page_num,
            "content": narrative_content,
            "tables": tables
        }

    def _parse_markdown_table(self, md_table: str, parent_section_id: str) -> Optional[dict]:
        """마크다운 테이블을 구조화된 JSON으로 변환"""
        lines = [l.strip() for l in md_table.strip().split('\n') if l.strip()]

        # 최소 3줄 필요 (헤더, 구분선, 데이터)
        if len(lines) < 3:
            return None

        # 헤더 파싱
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('|')[1:-1]]

        if not headers:
            return None

        # 데이터 행 파싱 (구분선 건너뛰기)
        rows_data = []
        for row_line in lines[2:]:
            cells = [c.strip() for c in row_line.split('|')[1:-1]]

            # 헤더 길이에 맞추기
            if len(cells) < len(headers):
                cells.extend([''] * (len(headers) - len(cells)))
            elif len(cells) > len(headers):
                cells = cells[:len(headers)]

            row_dict = {headers[i]: cells[i] for i in range(len(headers))}
            rows_data.append(row_dict)

        # 테이블 ID
        table_id = f"tbl_{self.table_id_counter:03d}"
        self.table_id_counter += 1

        # 구조화된 데이터 추출
        structured = self._auto_structure_table(rows_data, headers)

        # Q&A 쌍 생성
        qa_pairs = self._generate_qa_pairs(rows_data, headers)

        return {
            "table_id": table_id,
            "table_caption": self._infer_table_caption(headers),
            "headers": headers,
            "rows": rows_data,
            "structured_data": structured,
            "markdown": md_table,
            "queryable_facts": qa_pairs,
            "parent_section_id": parent_section_id
        }

    def _auto_structure_table(self, rows: List[dict], headers: List[str]) -> dict:
        """테이블에서 구조화 데이터 자동 추출"""
        structured = {}

        for row in rows:
            for key, value in row.items():
                # 키 정규화
                normalized_key = key.replace(' ', '_').replace('/', '_')

                # 숫자/비율 추출
                if '%' in value or any(char.isdigit() for char in value):
                    numbers = re.findall(r'\d+\.?\d*', value)

                    if numbers:
                        if normalized_key not in structured:
                            structured[normalized_key] = []

                        # 백분율이면 정수, 아니면 실수
                        num_value = float(numbers[0])
                        if '%' in value:
                            num_value = int(num_value)

                        structured[normalized_key].append(num_value)

                # 텍스트 리스트 구성
                elif value and not value.startswith('-'):
                    text_key = f"{normalized_key}_list"
                    if text_key not in structured:
                        structured[text_key] = []

                    # 쉼표로 분리된 항목 처리
                    items = [item.strip() for item in value.split(',')]
                    structured[text_key].extend(items)

        # 중복 제거
        for key in structured:
            if isinstance(structured[key], list):
                structured[key] = list(dict.fromkeys(structured[key]))

        return structured

    def _generate_qa_pairs(self, rows: List[dict], headers: List[str]) -> List[dict]:
        """자주 묻는 질문 자동 생성"""
        qa_pairs = []

        for row in rows:
            for key, value in row.items():
                if not value or value == '-':
                    continue

                # 비율/점수 관련 질문
                if '%' in value or '점' in value:
                    qa_pairs.append({
                        "question": f"{key}은 얼마인가요?",
                        "answer": value,
                        "source": "table",
                        "confidence": 1.0
                    })

                # 시기/날짜 관련 질문
                if any(word in key for word in ['시기', '날짜', '일정']):
                    qa_pairs.append({
                        "question": f"{key}는 언제인가요?",
                        "answer": value,
                        "source": "table",
                        "confidence": 1.0
                    })

        return qa_pairs

    def _infer_table_caption(self, headers: List[str]) -> str:
        """헤더로부터 테이블 제목 추론"""
        caption = " 및 ".join(headers[:3])
        return caption

    def _generate_document_id(self, metadata: dict) -> str:
        """문서 고유 ID 생성"""
        school_code = metadata.get('school_code', 'UNKNOWN')
        year = metadata.get('year', '0000')
        grade = metadata.get('grade', '0')
        subject = metadata.get('subject', 'general')
        semester = metadata.get('semester', '0')

        return f"doc_{school_code}_{year}_{grade}_{subject}_{semester}"

    def _generate_rag_metadata(self, sections: List[dict], doc_id: str) -> dict:
        """RAG 최적화 메타데이터 생성"""
        chunk_mappings = {}

        for section in sections:
            chunk_id = f"chunk_{section['section_id']}"
            chunk_mappings[chunk_id] = {
                "section": section['section_id'],
                "tables": [t['table_id'] for t in section['tables']],
                "type": section['section_type']
            }

        return {
            "chunk_strategy": "section_based",
            "chunk_ids": list(chunk_mappings.keys()),
            "chunk_mappings": chunk_mappings,
            "parent_document_id": doc_id,
            "supports_hierarchical_retrieval": True
        }
