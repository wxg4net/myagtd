;; yagtd-mode.el
;; Major mode for editing yaGTD files.
;; Copyright (C) 2007 MiKael NAVARRO

;; Author: MiKael Navarro <klnavarro@gmail.com>
;; Keywords: gtd, emacs, tools

;; This file is NOT part of GNU Emacs.

;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation; either version 2 of the License, or
;; (at your option) any later version.
;;
;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.
;;
;; You should have received a copy of the GNU General Public License
;; along with this program; if not, write to the Free Software
;; Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

;; Commentary:

;; yagtd-mode is a mode for editing to-do list.

;; Copy file "yagtd-mode.el" in one of the standard directories
;; where Emacs looks for elisp files (see Emacs's variable "load-path"
;; for a list of these paths, e.g., "/usr/local/share/emacs/site-lisp").
;;
;; Optionally byte-compile "yagtd-mode.el" (see Emacs's doc). 
;;
;; Insert the following lines in your "~/.emacs":
;;
;; (autoload 'yagtd-mode "yagtd-mode" "yaGTD mode" t)
;; (add-to-list 'auto-mode-alist '("\\.yagtd$" . yagtd-mode))

;; To show your personal todo-list:
;; M-x yagtd-mode
;;
;; For information on keybindings:
;; C-h f yagtd-mode RET
;;
;; Customize your yagtd with:
;; M-x customize-group RET yagtd RET

;;
;; User defined variables.
;;

(defgroup yagtd nil
  "*Major mode for editing yaGTD files."
  :group 'gtd
  :group 'emacs
  :group 'tools)

(defcustom yagtd-context-marker "@"
  "*String used to indicate a context."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-project-marker "p:"
  "*String used to indicate a project."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-status-marker "!"
  "*String used to indicate a status."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-reference-marker "ref:"
  "*String used to indicate a reference."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-urgency-marker "U:"
  "*String used to indicate an urgency flag."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-importance-marker "I:"
  "*String used to indicate an importance flag."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-complete-marker "C:"
  "*String used to indicate a percent complete."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-time-marker "T:"
  "*String used to indicate a time requiered."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-recurrence-marker "R:"
  "*String used to indicate a recurrence."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-start-marker "S:"
  "*String used to indicate a start/creation date."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-due-marker "D:"
  "*String used to indicate a due (target) date."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-end-marker "E:"
  "*String used to indicate a closure date."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-word-matcher "[A-Za-z0-9_-]+"
  "*String used to indicate a word."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-digit-matcher "[1-5]"
  "*String used to indicate a digit."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-number-matcher "[0-9]+"
  "*String used to indicate a number."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-duration-matcher "[0-9]+[WDHM]"
  "*String used to indicate a duration or a recurrence."
  :type 'string
  :group 'yagtd)

(defcustom yagtd-date-matcher "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]"
  "*String used to indicate a date."
  :type 'string
  :group 'yagtd)

(defvar yagtd-context-matcher (concat yagtd-context-marker yagtd-word-matcher))
(defvar yagtd-project-matcher (concat yagtd-project-marker yagtd-word-matcher))
(defvar yagtd-status-matcher (concat yagtd-status-marker yagtd-word-matcher))
(defvar yagtd-reference-matcher (concat yagtd-reference-marker yagtd-word-matcher))

(defvar yagtd-urgency-matcher (concat yagtd-urgency-marker yagtd-digit-matcher))
(defvar yagtd-importance-matcher (concat yagtd-importance-marker yagtd-digit-matcher))
(defvar yagtd-complete-matcher (concat yagtd-complete-marker yagtd-number-matcher))

(defvar yagtd-time-matcher (concat yagtd-time-marker yagtd-duration-matcher))
(defvar yagtd-recurrence-matcher (concat yagtd-recurrence-marker yagtd-duration-matcher))

(defvar yagtd-start-matcher (concat yagtd-start-marker yagtd-date-matcher))
(defvar yagtd-due-matcher (concat yagtd-due-marker yagtd-date-matcher))
(defvar yagtd-end-matcher (concat yagtd-end-marker yagtd-date-matcher))

;;
;; Internal variables.
;;

;; Allows the user to run their own code when your mode is run.
(defvar yagtd-mode-hook nil)

;; Allows both you and users to define their own keymaps.
(defvar yagtd-mode-map
  (let ((yagtd-mode-map (make-keymap)))
    (define-key yagtd-mode-map "\C-j" 'newline-and-indent)
    yagtd-mode-map)
  "Keymap for yaGTD major mode")

;(add-to-list 'auto-mode-alist '("\\.yagtd$" . yagtd-mode))

;;
;; Font Lock mode faces.
;;

(defface yagtd-context-face 
     '((t (:foreground "yellow2" :bold t)))  ; dark_yellow
   "Font Lock mode face used to highlight context-keywords.")

(defface yagtd-project-face 
     '((t (:foreground "purple" :bold t)))  ; dark_purple
   "Font Lock mode face used to highlight project-keywords.")

(defface yagtd-status-face 
     '((t (:foreground "green" :bold t)))  ; dark_green
   "Font Lock mode face used to highlight status-keywords.")

(defface yagtd-reference-face 
     '((t (:foreground "blue" :bold t)))  ; dark_blue
   "Font Lock mode face used to highlight reference-keywords.")

(defface yagtd-urgency-face 
     '((t (:foreground "red" :bold t)))  ; red
   "Font Lock mode face used to highlight urgency-keywords.")

(defface yagtd-importance-face 
     '((t (:foreground "red" :bold t)))  ; red
   "Font Lock mode face used to highlight importance-keywords.")

(defface yagtd-complete-face 
     '((t (:foreground "white" :bold t)))  ; white
   "Font Lock mode face used to highlight complete-keywords.")

(defface yagtd-time-face 
     '((t (:foreground "cyan" :normal t)))  ; cyan
   "Font Lock mode face used to highlight time-keywords.")

(defface yagtd-recurrence-face 
     '((t (:foreground "cyan" :normal t)))  ; cyan
   "Font Lock mode face used to highlight recurrence-keywords.")

(defface yagtd-start-face 
     '((t (:foreground "red" :normal t)))  ; red
   "Font Lock mode face used to highlight start-keywords.")

(defface yagtd-due-face 
     '((t (:foreground "red" :normal t)))  ; red
   "Font Lock mode face used to highlight due-keywords.")

(defface yagtd-end-face 
     '((t (:foreground "green" :normal t)))  ; green
   "Font Lock mode face used to highlight end-keywords.")

;; Minimal set of keywords for emacs to highlight.
(defconst yagtd-font-lock-keywords-1
  (list
   ;; These define each GTD entity
   (list yagtd-context-matcher '(0 'yagtd-context-face t))
   (list yagtd-project-matcher '(0 'yagtd-project-face t))
   (list yagtd-status-matcher '(0 'yagtd-status-face t))
   (list yagtd-reference-matcher '(0 'yagtd-reference-face t))
   ;; Urgency and priotities
   (list yagtd-urgency-matcher '(0 'yagtd-urgency-face t))
   (list yagtd-importance-matcher '(0 'yagtd-importance-face t))
   (list yagtd-complete-matcher '(0 'yagtd-complete-face t))
   )
  "Minimal highlighting expressions for yaGTD mode.")

;; Additional set of keywords for emacs to highlight.
(defconst yagtd-font-lock-keywords-2
  (append yagtd-font-lock-keywords-1
	  (list
	   ;; Durations
	   (list yagtd-time-matcher '(0 'yagtd-time-face t))
	   (list yagtd-recurrence-matcher '(0 'yagtd-recurrence-face t))
	   ;; Dates
	   (list yagtd-start-matcher '(0 'yagtd-start-face t))
	   (list yagtd-due-matcher '(0 'yagtd-due-face t))
	   (list yagtd-end-matcher '(0 'yagtd-end-face t))
	   )
	  )
  "Additional keywords to highlight in yaGTD mode.")

;; More additional set of keywords for emacs to highlight.
(defconst yagtd-font-lock-keywords-3
  (append yagtd-font-lock-keywords-2
	  (
	   ;; Test
	   ;(list yagtd-context-matcher '(0 'yagtd-context-face t))
	   )
	  )
  "More additional keywords to highlight in yaGTD mode.")

;; Here I've defined the default level of highlighting to be the maximum.
(defvar yagtd-font-lock-keywords yagtd-font-lock-keywords-3
  "Default highlighting expressions for yaGTD mode.")

;; We will use the make-syntax-table function to create an empty
;; syntax table.  This function creates a syntax table that is a good
;; start for most modes, as it either inherits or copies entries from
;; the standard syntax table.
(defvar yagtd-mode-syntax-table
  (let ((yagtd-mode-syntax-table (make-syntax-table)))
    ;; This is added so entity names with underscores can be more easily parsed.
    (modify-syntax-entry ?_ "w" yagtd-mode-syntax-table)
    ;; Comment styles are same as Python.
    (modify-syntax-entry ?# "<" yagtd-mode-syntax-table)
    (modify-syntax-entry ?\n ">" yagtd-mode-syntax-table)
    yagtd-mode-syntax-table)
  "Syntax table for yagtd-mode")
  
;;
;; Main function.
;;
;;;###autoload
(defun yagtd-mode ()
  (interactive)
  (kill-all-local-variables)
  (use-local-map yagtd-mode-map)
  (set-syntax-table yagtd-mode-syntax-table)
  ;; Set up font-lock.
  (set (make-local-variable 'font-lock-defaults) '(yagtd-font-lock-keywords))
  ;; Register our indentation function.
  ;(set (make-local-variable 'indent-line-function) 'yagtd-indent-line)  
  (setq major-mode 'yagtd-mode)
  (setq mode-name "yaGTD")
  (run-hooks 'yagtd-mode-hook))

; This can replace (defun yagtd-mode ()...
;(define-derived-mode yagtd-mode fundamental-mode "yaGTD"
;  "Major mode for editing yaGTD to-do lists."
;  (set (make-local-variable 'font-lock-defaults) '(yagtd-font-lock-keywords))
;  (set (make-local-variable 'indent-line-function) 'yagtd-indent-line)
;  )

(provide 'yagtd-mode)
;; yagyd-mode.el ends here.
