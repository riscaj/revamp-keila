from pathlib import Path

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select, WebDriverWait

from src.pages.transactions.reklasifikasi import reklasifikasi_locators as locators


APPLICATION_DOCUMENT = (
    Path(__file__).resolve().parents[4]
    / "Upload_Pengajuan"
    / "Pdf test file.pdf"
)


class PengajuanKreditBermasalahPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            30,
            poll_frequency=0.5,
            ignored_exceptions=(StaleElementReferenceException,),
        )

    def enter_credit_number(self, credit_number):
        credit_field = self.wait.until(
            lambda driver: self._find_field(driver, locators.CREDIT_NUMBER_LOCATOR),
            "Field nomor kredit tidak ditemukan pada pengajuan Reklas Kredit Bermasalah.",
        )
        credit_field.clear()
        credit_field.send_keys(credit_number)

    def choose_application_type(self, application_type):
        self._choose_option("Jenis Pengajuan", application_type)

    def search_credit_number(self):
        self._click_button("Cari Nomor Kredit")
        self.wait.until(
            lambda driver: self._find_checkbox_option(driver, "Kerusuhan"),
            "Checkbox opsi 'Kerusuhan' tidak tampil setelah pencarian nomor kredit.",
        )

    def choose_problem_criterion(self, criterion):
        checkbox = self.wait.until(
            lambda driver: self._find_checkbox_option(driver, criterion),
            f"Checkbox kriteria {criterion!r} tidak ditemukan.",
        )
        if not self._checkbox_is_selected(self.driver, checkbox):
            self._click(checkbox)
        self.wait.until(
            lambda driver: self._checkbox_is_selected(driver, checkbox),
            f"Checkbox kriteria {criterion!r} belum tercentang.",
        )

    def fill_problem_note(self, note):
        field = self.wait.until(
            lambda driver: self._find_editable_labeled_field(
                driver, "Catatan Pinjaman Bermasalah"
            ),
            "Field Catatan Pinjaman Bermasalah yang bisa diedit tidak ditemukan.",
        )
        self._click(field)
        field.clear()
        field.send_keys(note)
        self.wait.until(
            lambda driver: field.get_property("value") == note,
            "Catatan Pinjaman Bermasalah belum terisi.",
        )

    def upload_supporting_document(self, document_name):
        if not APPLICATION_DOCUMENT.is_file():
            raise FileNotFoundError(
                f"File PDF pengajuan tidak ditemukan: {APPLICATION_DOCUMENT}"
            )
        if APPLICATION_DOCUMENT.suffix.casefold() != ".pdf":
            raise ValueError(
                f"Dokumen pendukung pengajuan harus berformat PDF: "
                f"{APPLICATION_DOCUMENT}"
            )
        if APPLICATION_DOCUMENT.stat().st_size > 5 * 1024 * 1024:
            raise ValueError(
                f"Ukuran PDF dokumen pendukung melebihi batas 5 MB: "
                f"{APPLICATION_DOCUMENT}"
            )

        self._click_text("pilih dari perangkat")
        self.wait.until(
            lambda driver: self._find_supporting_document_dialog(driver),
            "Popup Dokumen Pendukung tidak tampil setelah memilih upload.",
        )

        name_field = self.wait.until(
            lambda driver: self._find_document_name_field(driver),
            "Field Nama Dokumen tidak ditemukan di popup Dokumen Pendukung.",
        )
        self._click(name_field)
        name_field.clear()
        name_field.send_keys(document_name)
        self.wait.until(
            lambda driver: name_field.get_property("value") == document_name,
            "Nama dokumen belum terisi pada popup Dokumen Pendukung.",
        )

        choose_file_text = self.wait.until(
            lambda driver: self._find_text_in_supporting_dialog(
                driver, "pilih dari perangkat"
            ),
            "Tombol pilih dari perangkat tidak ditemukan di popup Dokumen Pendukung.",
        )
        self._click(choose_file_text)
        file_input = self.wait.until(
            lambda driver: self._find_document_file_input(driver),
            "Input file PDF tidak ditemukan di popup Dokumen Pendukung.",
        )
        file_input.send_keys(str(APPLICATION_DOCUMENT))
        self.wait.until(
            lambda driver: self._document_file_is_selected(driver),
            "File PDF belum terpasang pada dokumen pendukung.",
        )
        self._click_button_in_supporting_dialog("Tambah")
        self.wait.until(
            lambda driver: not self._find_supporting_document_dialog(driver),
            "Popup Dokumen Pendukung tidak tertutup setelah menekan Tambah.",
        )

    def submit_and_finish(self):
        self._click_button("Proses Pengajuan")
        confirmation_labels = ("Ya, Lanjukan", "Ya, Lanjutkan")
        self._click_button_any(confirmation_labels)
        self.wait.until(
            lambda driver: not self._find_visible_button_any(
                driver, confirmation_labels
            ),
            "Modal konfirmasi Ya, Lanjukan tidak tertutup.",
        )
        self._click_button("Selesai")

    def _choose_option(self, field_label, option_label):
        field = self.wait.until(
            lambda driver: self._find_application_type_control(driver, field_label),
            f"Dropdown {field_label} tidak ditemukan.",
        )
        if field.tag_name.casefold() == "select":
            select = Select(field)
            select.select_by_visible_text(option_label)
            self.wait.until(
                lambda driver: self._native_option_is_selected(
                    driver, field, option_label
                ),
                f"Opsi {option_label!r} belum terpilih pada {field_label}.",
            )
            return

        self._click(field)
        option = self.wait.until(
            lambda driver: self._find_visible_option(driver, option_label),
            f"Opsi {option_label!r} tidak tampil pada dropdown {field_label}.",
        )
        self._click(option)
        self.wait.until(
            lambda driver: self._custom_option_is_selected(
                driver, field, option_label
            ),
            f"Opsi {option_label!r} belum terpilih pada {field_label}.",
        )

    @staticmethod
    def _find_field(driver, locator):
        for field in driver.find_elements(*locator):
            if field.is_displayed() and field.is_enabled():
                return field
        return False

    @staticmethod
    def _find_labeled_control(driver, label):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            const expected = normalize(arguments[0]);
            const visible = element => {
                if (!element || element.tagName === 'HTML' || element.tagName === 'BODY') return false;
                const rect = element.getBoundingClientRect ? element.getBoundingClientRect() : null;
                if (rect && rect.width === 0 && rect.height === 0 && !element.getAttribute('aria-label')) {
                    return false;
                }
                const style = window.getComputedStyle(element);
                return style.visibility !== 'hidden' && style.display !== 'none' && style.opacity !== '0';
            };
            const textFrom = element => (element?.innerText || element?.textContent || element?.value || '').trim();
            const getTextContext = element => {
                const labels = [...(element.labels || [])].map(item => textFrom(item));
                const info = [
                    ...labels,
                    element.getAttribute('aria-label') || '',
                    element.getAttribute('placeholder') || '',
                    element.getAttribute('name') || '',
                    element.id || '',
                    textFrom(element),
                ];
                let parent = element.parentElement;
                for (let i = 0; i < 5 && parent; i += 1) {
                    info.push(textFrom(parent));
                    parent = parent.parentElement;
                }
                return info.join(' ');
            };

            const controlSelectors = [
                'select',
                'input:not([type="file"])',
                'textarea',
                'button',
                '[role="combobox"]',
                '[role="button"]',
                '[aria-haspopup="listbox"]',
                '[aria-labelledby]',
                '[aria-label]',
                '.ant-select-selector',
                '.select-control',
                '[class*="select"]',
                '[class*="dropdown"]',
                'div',
                'span'
            ];

            const candidates = [...document.querySelectorAll(controlSelectors.join(','))]
                .filter(visible)
                .map(element => ({element, score: normalize(getTextContext(element)).includes(expected) ? 0 : 2}))
                .filter(item => item.score === 0)
                .sort((left, right) => left.score - right.score);

            if (candidates.length) {
                return candidates[0].element;
            }

            const textMatches = [...document.querySelectorAll('*')]
                .filter(element => visible(element) && normalize(textFrom(element)).includes(expected))
                .find(element => element.tagName !== 'BODY');
            if (textMatches) {
                const container = textMatches.closest('[class*="form"], [class*="field"], label, div, span');
                if (container) {
                    const control = container.querySelector(
                        'select, input:not([type="file"]), textarea, button, [role="combobox"], [role="button"], [aria-haspopup="listbox"], [class*="select"], [class*="dropdown"]'
                    );
                    if (control) return control;
                    return container;
                }
                return textMatches;
            }

            return false;
            """,
            label,
        )

    @staticmethod
    def _find_editable_labeled_field(driver, label):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            const expected = normalize(arguments[0]);
            const visible = element => {
                const style = window.getComputedStyle(element);
                return style.display !== 'none' && style.visibility !== 'hidden' &&
                    style.opacity !== '0' && element.getClientRects().length > 0;
            };
            const editable = element =>
                visible(element) && !element.disabled && !element.readOnly &&
                element.getAttribute('aria-disabled') !== 'true' &&
                element.matches('textarea, input:not([type="hidden"])');
            const fieldSelector = 'textarea, input:not([type="hidden"])';
            const textFrom = element =>
                (element?.innerText || element?.textContent || '').trim();
            const labels = [...document.querySelectorAll('label, span, div, p')]
                .filter(element => visible(element) &&
                    normalize(textFrom(element)) === expected)
                .sort((left, right) =>
                    left.querySelectorAll('*').length - right.querySelectorAll('*').length
                );

            for (const labelNode of labels) {
                if (labelNode.matches('label[for]')) {
                    const associated = document.getElementById(
                        labelNode.getAttribute('for')
                    );
                    if (associated && editable(associated)) return associated;
                }
                let container = labelNode;
                for (let depth = 0; depth < 6 && container; depth += 1) {
                    const fields = [...container.querySelectorAll(fieldSelector)]
                        .filter(editable);
                    if (fields.length === 1) return fields[0];
                    if (fields.length > 1) {
                        const textarea = fields.find(field => field.matches('textarea'));
                        if (textarea) return textarea;
                    }
                    container = container.parentElement;
                }
            }

            const namedFields = [...document.querySelectorAll(fieldSelector)]
                .filter(editable)
                .filter(field => {
                    const metadata = [
                        field.getAttribute('aria-label') || '',
                        field.getAttribute('placeholder') || '',
                        field.getAttribute('name') || '',
                        field.id || '',
                        ...Array.from(field.labels || []).map(textFrom),
                    ];
                    return metadata.some(value => normalize(value).includes(expected));
                });
            return namedFields[0] || false;
            """,
            label,
        )

    @staticmethod
    def _find_application_type_control(driver, label):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            const expected = normalize(arguments[0]);
            const visible = element => {
                const style = window.getComputedStyle(element);
                return style.display !== 'none' && style.visibility !== 'hidden' &&
                    style.opacity !== '0' && element.getClientRects().length > 0;
            };
            const labelNodes = [...document.querySelectorAll('label, span, div, p')]
                .filter(element => visible(element) &&
                    normalize(element.innerText || element.textContent) === expected)
                .sort((left, right) =>
                    left.querySelectorAll('*').length - right.querySelectorAll('*').length
                );
            const triggerSelector = [
                'select',
                '[role="combobox"]',
                '[aria-haspopup="listbox"]',
                'input:not([type="hidden"])',
                'button',
                '[class*="select"]'
            ].join(',');

            for (const labelNode of labelNodes) {
                let container = labelNode;
                for (let depth = 0; depth < 6 && container; depth += 1) {
                    const candidates = [...container.querySelectorAll(triggerSelector)]
                        .filter(control => control !== labelNode && visible(control));
                    if (candidates.length === 1) return candidates[0];
                    if (candidates.length > 1) {
                        const select = candidates.find(control =>
                            control.matches('select, [role="combobox"], [aria-haspopup="listbox"]') ||
                            control.className?.toString().toLocaleLowerCase().includes('select')
                        );
                        if (select) return select;
                    }
                    container = container.parentElement;
                }
            }
            return false;
            """,
            label,
        )

    @staticmethod
    def _find_visible_option(driver, option_label):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            const expected = normalize(arguments[0]);
            const visible = element => {
                const style = window.getComputedStyle(element);
                return style.display !== 'none' && style.visibility !== 'hidden' &&
                    style.opacity !== '0' && element.getClientRects().length > 0;
            };
            const candidates = [...document.querySelectorAll(
                '[role="option"], [role="menuitem"], option, li, button, label, div, span'
            )].filter(element => visible(element) &&
                normalize(element.innerText || element.textContent) === expected);
            candidates.sort((left, right) =>
                left.querySelectorAll('*').length - right.querySelectorAll('*').length
            );
            return candidates[0] || false;
            """,
            option_label,
        )

    @staticmethod
    def _custom_option_is_selected(driver, field, option_label):
        return driver.execute_script(
            """
            const field = arguments[0];
            const expected = (arguments[1] || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            if (field.matches('input, textarea')) {
                return normalize(field.value) === expected;
            }
            return [
                field.innerText,
                field.textContent,
                field.getAttribute('aria-valuetext'),
                field.getAttribute('aria-label'),
                field.getAttribute('title')
            ].some(value => normalize(value).includes(expected));
            """,
            field,
            option_label,
        )

    @staticmethod
    def _find_checkbox_option(driver, option_label):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            const expected = normalize(arguments[0]);
            const textFrom = element =>
                (element?.innerText || element?.textContent || '').trim();
            const visible = element => {
                const style = window.getComputedStyle(element);
                return style.display !== 'none' && style.visibility !== 'hidden' &&
                    style.opacity !== '0';
            };
            const checkboxSelector = 'input[type="checkbox"], [role="checkbox"]';
            const labeledControls = [...document.querySelectorAll(checkboxSelector)]
                .map(control => {
                    const labels = [
                        ...Array.from(control.labels || []).map(textFrom),
                        control.getAttribute('aria-label') || '',
                        control.getAttribute('aria-labelledby')
                            ? textFrom(document.getElementById(
                                control.getAttribute('aria-labelledby')
                            ))
                            : '',
                    ];
                    const matchingLabel = labels.some(label =>
                        normalize(label) === expected ||
                        normalize(label).startsWith(expected + ' ')
                    );
                    return {control, matchingLabel};
                })
                .filter(item => item.matchingLabel);
            if (labeledControls.length) return labeledControls[0].control;

            const optionText = [...document.querySelectorAll('label, [role="checkbox"], span, div')]
                .filter(element => visible(element) &&
                    normalize(textFrom(element)) === expected)
                .sort((left, right) => {
                    const leftChildren = left.querySelectorAll('*').length;
                    const rightChildren = right.querySelectorAll('*').length;
                    return leftChildren - rightChildren;
                })[0];
            if (optionText) {
                if (optionText.matches(checkboxSelector)) return optionText;
                if (optionText.matches('label')) {
                    const control = optionText.control || optionText.querySelector(checkboxSelector);
                    if (control) return control;
                }
                let container = optionText;
                for (let depth = 0; depth < 3 && container; depth += 1) {
                    const control = container.querySelector(checkboxSelector);
                    if (control) return control;
                    container = container.parentElement;
                }
                if (optionText.closest('label')) {
                    const control = optionText.closest('label').querySelector(checkboxSelector);
                    if (control) return control;
                }
                if (optionText.getAttribute('role') === 'checkbox') return optionText;
            }
            return false;
            """,
            option_label,
        )

    @staticmethod
    def _checkbox_is_selected(driver, checkbox):
        return driver.execute_script(
            """
            const element = arguments[0];
            if (element.matches('input[type="checkbox"]')) return element.checked;
            return element.getAttribute('aria-checked') === 'true';
            """,
            checkbox,
        )

    def _click_text(self, text):
        element = self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const expected = normalize(arguments[0]);
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const matches = [...document.querySelectorAll('body *')].filter(
                    element => visible(element) &&
                        normalize(element.innerText || element.textContent) === expected
                );
                const leaves = matches.filter(element =>
                    ![...element.children].some(child =>
                        normalize(child.innerText || child.textContent) === expected
                    )
                );
                const candidates = leaves.length ? leaves : matches;
                candidates.sort((left, right) => {
                    const leftRect = left.getBoundingClientRect();
                    const rightRect = right.getBoundingClientRect();
                    return leftRect.width * leftRect.height -
                        rightRect.width * rightRect.height;
                });
                return candidates[0] || false;
                """,
                text,
            ),
            f"Opsi {text!r} tidak ditemukan.",
        )
        self._click(element)

    def _click_button(self, label):
        button = self.wait.until(
            lambda driver: self._find_enabled_button(driver, label),
            f"Tombol {label!r} tidak ditemukan atau tidak aktif.",
        )
        self._click(button)

    def _click_button_any(self, labels):
        button = self.wait.until(
            lambda driver: self._find_visible_button_any(driver, labels),
            f"Tombol konfirmasi {labels!r} tidak ditemukan atau tidak aktif.",
        )
        self._click(button)

    def _find_enabled_button(self, driver, label):
        button = self._find_visible_button(driver, label)
        if button and button.is_enabled():
            return button
        return False

    @staticmethod
    def _find_visible_button(driver, label):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const expected = normalize(arguments[0]).toLocaleLowerCase();
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            return [...document.querySelectorAll(
                'button, [role="button"], input[type="button"], input[type="submit"]'
            )].find(element =>
                visible(element) &&
                normalize(element.innerText || element.value || '')
                    .toLocaleLowerCase() === expected &&
                !element.disabled &&
                element.getAttribute('aria-disabled') !== 'true'
            ) || false;
            """,
            label,
        )

    def _find_visible_button_any(self, driver, labels):
        return next(
            (
                button
                for label in labels
                if (button := self._find_visible_button(driver, label))
            ),
            False,
        )

    @staticmethod
    def _find_supporting_document_dialog(driver):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            const visible = element => {
                const style = window.getComputedStyle(element);
                return style.display !== 'none' && style.visibility !== 'hidden' &&
                    style.opacity !== '0' && element.getClientRects().length > 0;
            };
            const headings = [...document.querySelectorAll('h1, h2, h3, h4, strong, div, span')]
                .filter(element => visible(element) &&
                    normalize(element.innerText || element.textContent) === 'dokumen pendukung')
                .sort((left, right) =>
                    left.querySelectorAll('*').length - right.querySelectorAll('*').length
                );
            for (const heading of headings) {
                let container = heading;
                for (let depth = 0; depth < 8 && container; depth += 1) {
                    const hasNameField = container.querySelector(
                        'input[placeholder="Masukkan nama dokumen"], input:not([type="file"])'
                    );
                    const hasAddButton = [...container.querySelectorAll(
                        'button, [role="button"]'
                    )].some(button =>
                        normalize(button.innerText || button.textContent) === 'tambah'
                    );
                    if (hasNameField && hasAddButton) return container;
                    container = container.parentElement;
                }
            }
            return false;
            """
        )

    @staticmethod
    def _find_document_name_field(driver):
        return driver.execute_script(
            """
            const root = arguments[0];
            if (!root) return false;
            const visible = element => {
                const style = window.getComputedStyle(element);
                return style.display !== 'none' && style.visibility !== 'hidden' &&
                    style.opacity !== '0' && element.getClientRects().length > 0;
            };
            return [...root.querySelectorAll('input:not([type="file"]), textarea')]
                .find(field => visible(field) && !field.disabled && !field.readOnly &&
                    (field.getAttribute('placeholder') || '').trim()
                        .toLocaleLowerCase() === 'masukkan nama dokumen') || false;
            """,
            PengajuanKreditBermasalahPage._find_supporting_document_dialog(driver),
        )

    @staticmethod
    def _find_text_in_supporting_dialog(driver, text):
        return driver.execute_script(
            """
            const root = arguments[0];
            if (!root) return false;
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            const expected = normalize(arguments[1]);
            const visible = element => {
                const style = window.getComputedStyle(element);
                return style.display !== 'none' && style.visibility !== 'hidden' &&
                    style.opacity !== '0' && element.getClientRects().length > 0;
            };
            const matches = [...root.querySelectorAll('button, label, span, div')]
                .filter(element => visible(element) &&
                    normalize(element.innerText || element.textContent).includes(expected))
                .sort((left, right) =>
                    (left.innerText || left.textContent).trim().length -
                        (right.innerText || right.textContent).trim().length ||
                    left.querySelectorAll('*').length - right.querySelectorAll('*').length
                );
            return matches[0] || false;
            """,
            PengajuanKreditBermasalahPage._find_supporting_document_dialog(driver),
            text,
        )

    def _click_button_in_supporting_dialog(self, label):
        button = self.wait.until(
            lambda driver: driver.execute_script(
                """
                const root = arguments[0];
                if (!root) return false;
                const expected = (arguments[1] || '').trim().replace(/\\s+/g, ' ')
                    .toLocaleLowerCase();
                const visible = element => {
                    const style = window.getComputedStyle(element);
                    return style.display !== 'none' && style.visibility !== 'hidden' &&
                        style.opacity !== '0' && element.getClientRects().length > 0;
                };
                return [...root.querySelectorAll('button, [role="button"]')]
                    .find(button => visible(button) && !button.disabled &&
                        (button.getAttribute('aria-disabled') || '') !== 'true' &&
                        (button.innerText || button.textContent || '').trim()
                            .replace(/\\s+/g, ' ').toLocaleLowerCase() === expected) || false;
                """,
                self._find_supporting_document_dialog(driver),
                label,
            ),
            f"Tombol {label!r} tidak ditemukan atau tidak aktif di popup Dokumen Pendukung.",
        )
        self._click(button)

    @staticmethod
    def _native_option_is_selected(driver, field, option_label):
        return driver.execute_script(
            """
            return arguments[0].selectedOptions.length === 1 &&
                arguments[0].selectedOptions[0].text.trim() === arguments[1];
            """,
            field,
            option_label,
        )

    @staticmethod
    def _find_document_file_input(driver):
        return driver.execute_script(
            """
            const root = arguments[0];
            if (!root) return false;
            const inputs = [...root.querySelectorAll('input[type="file"]')];
            return inputs[0] || false;
            """,
            PengajuanKreditBermasalahPage._find_supporting_document_dialog(driver),
        )

    @staticmethod
    def _document_file_is_selected(driver):
        return driver.execute_script(
            """
            const root = arguments[0];
            if (!root) return false;
            const input = root.querySelector('input[type="file"]');
            return Boolean(input?.files.length) &&
                input.files[0].name === arguments[1];
            """,
            PengajuanKreditBermasalahPage._find_supporting_document_dialog(driver),
            APPLICATION_DOCUMENT.name,
        )

    def _click(self, element):
        self.driver.execute_script(
            """
            arguments[0].scrollIntoView({block: 'center', inline: 'center'});
            arguments[0].click();
            """,
            element,
        )
