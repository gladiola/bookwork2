#!/usr/bin/env Rscript

required_packages <- c(
  "readxl",
  "dplyr",
  "tidyr",
  "lmerTest",
  "emmeans",
  "ggplot2",
  "openxlsx"
)

missing_packages <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages) > 0) {
  stop(
    sprintf(
      "Missing required packages: %s\nInstall them first, then rerun the script.",
      paste(missing_packages, collapse = ", ")
    ),
    call. = FALSE
  )
}

suppressPackageStartupMessages({
  library(readxl)
  library(dplyr)
  library(tidyr)
  library(lmerTest)
  library(emmeans)
  library(ggplot2)
  library(openxlsx)
})

category_levels <- c(
  "Data Breach",
  "Personal Data Breach",
  "Malware",
  "Phishing",
  "Ransomware",
  "Crimes Against Children",
  "Extortion",
  "Threats/Stalking/Harassment/Terrorism",
  "IPR/Counterfeit",
  "Identity Theft",
  "BEC"
)

sheet_map <- c(
  AS = "City Summary AMERICAN_SAMOA",
  TN = "City Summary",
  CA = "City Summary CALIFORNIA"
)

workbook_name <- "ComputerCrime_AUG2026_Impact_Final_With_C5C7_IFERROR_CHARTS_FIXED_UPDATED.xlsx"

get_script_dir <- function() {
  file_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
  if (length(file_arg) > 0) {
    return(dirname(normalizePath(sub("^--file=", "", file_arg[[1]]))))
  }
  normalizePath(getwd())
}

parse_numeric_value <- function(x) {
  if (is.null(x) || length(x) == 0 || is.na(x)) {
    return(NA_real_)
  }

  if (is.character(x)) {
    value <- trimws(x)
    if (value == "" || grepl("^#", value)) {
      return(NA_real_)
    }
    value <- gsub("[,$]", "", value)
    parsed <- suppressWarnings(as.numeric(value))
    return(parsed)
  }

  suppressWarnings(as.numeric(x))
}

escape_latex <- function(x) {
  out <- as.character(x)
  out <- gsub("\\", "\\textbackslash{}", out, fixed = TRUE)

  replacements <- c(
    "&" = "\\&",
    "%" = "\\%",
    "$" = "\\$",
    "#" = "\\#",
    "_" = "\\_",
    "{" = "\\{",
    "}" = "\\}",
    "~" = "\\textasciitilde{}",
    "^" = "\\textasciicircum{}"
  )

  for (pattern in names(replacements)) {
    out <- gsub(pattern, replacements[[pattern]], out, fixed = TRUE)
  }
  out
}

format_number <- function(x, digits = 3) {
  ifelse(is.na(x), "NA", formatC(x, format = "f", digits = digits, big.mark = ","))
}

format_p_value <- function(x) {
  ifelse(is.na(x), "NA", ifelse(x < 0.001, "<0.001", formatC(x, format = "f", digits = 3)))
}

read_adjusted_rate_sheet <- function(path, sheet_name, state_code) {
  raw <- suppressMessages(
    read_excel(
      path = path,
      sheet = sheet_name,
      range = "B5:P11",
      col_names = FALSE,
      col_types = rep("text", 15)
    )
  )

  names(raw) <- c(
    "Year",
    "Population",
    "PopulationChange",
    "Crimes",
    category_levels
  )

  raw %>%
    mutate(
      State = state_code,
      Year = as.integer(Year),
      Population = vapply(Population, parse_numeric_value, numeric(1)),
      PopulationChange = vapply(PopulationChange, parse_numeric_value, numeric(1))
    ) %>%
    relocate(State)
}

build_long_data <- function(wide_data) {
  wide_data %>%
    pivot_longer(
      cols = all_of(category_levels),
      names_to = "Category",
      values_to = "AdjustedRateRaw"
    ) %>%
    mutate(
      AdjustedRate = vapply(AdjustedRateRaw, parse_numeric_value, numeric(1)),
      Category = factor(Category, levels = category_levels),
      State = factor(State, levels = c("AS", "TN", "CA")),
      Year = factor(Year)
    ) %>%
    select(State, Year, Category, Population, PopulationChange, AdjustedRate, AdjustedRateRaw)
}

to_clean_dataframe <- function(x, row_name_column = NULL) {
  df <- as.data.frame(x, stringsAsFactors = FALSE)
  if (!is.null(row_name_column) && !is.null(rownames(df))) {
    df[[row_name_column]] <- rownames(df)
    rownames(df) <- NULL
    df <- df[, c(row_name_column, setdiff(names(df), row_name_column))]
  }
  dplyr::as_tibble(df)
}

make_emm_plot <- function(emm_table, output_file) {
  plot_data <- emm_table %>%
    mutate(Category = factor(Category, levels = rev(category_levels)))

  ggplot(plot_data, aes(x = emmean, y = Category, shape = State, linetype = State)) +
    geom_vline(xintercept = 0, linewidth = 0.5, color = "gray40") +
    geom_errorbarh(
      aes(xmin = lower.CL, xmax = upper.CL),
      height = 0.25,
      position = position_dodge(width = 0.65),
      linewidth = 0.8
    ) +
    geom_point(position = position_dodge(width = 0.65), size = 3.5, fill = "white", stroke = 1.2) +
    scale_shape_manual(values = c(AS = 21, TN = 22, CA = 24)) +
    scale_linetype_manual(values = c(AS = "solid", TN = "dashed", CA = "dotted")) +
    labs(
      title = "Estimated marginal means with 95% confidence intervals",
      x = "Adjusted per-capita rate",
      y = NULL,
      shape = "State",
      linetype = "State"
    ) +
    theme_minimal(base_size = 16) +
    theme(
      legend.position = "top",
      panel.grid.major = element_line(color = "gray80", linewidth = 0.3),
      panel.grid.minor = element_blank(),
      axis.text = element_text(color = "black"),
      axis.title = element_text(color = "black"),
      plot.title = element_text(color = "black", hjust = 0.5),
      legend.text = element_text(size = 15),
      legend.title = element_text(size = 16)
    )

  ggsave(output_file, width = 10, height = 12, dpi = 300)
}

make_contrast_plot <- function(contrast_table, output_file) {
  plot_data <- contrast_table %>%
    mutate(
      Category = factor(Category, levels = rev(category_levels)),
      contrast = factor(contrast, levels = c("TN vs AS", "TN vs CA"))
    )

  ggplot(plot_data, aes(x = estimate, y = Category, shape = contrast, linetype = contrast)) +
    geom_vline(xintercept = 0, linewidth = 0.5, color = "gray40") +
    geom_errorbarh(
      aes(xmin = lower.CL, xmax = upper.CL),
      height = 0.25,
      position = position_dodge(width = 0.65),
      linewidth = 0.8
    ) +
    geom_point(position = position_dodge(width = 0.65), size = 3.5, fill = "white", stroke = 1.2) +
    scale_shape_manual(values = c("TN vs AS" = 22, "TN vs CA" = 24)) +
    scale_linetype_manual(values = c("TN vs AS" = "dashed", "TN vs CA" = "dotted")) +
    labs(
      title = "Planned contrasts with 95% confidence intervals",
      x = "Contrast estimate",
      y = NULL,
      shape = "Contrast",
      linetype = "Contrast"
    ) +
    theme_minimal(base_size = 16) +
    theme(
      legend.position = "top",
      panel.grid.major = element_line(color = "gray80", linewidth = 0.3),
      panel.grid.minor = element_blank(),
      axis.text = element_text(color = "black"),
      axis.title = element_text(color = "black"),
      plot.title = element_text(color = "black", hjust = 0.5),
      legend.text = element_text(size = 15),
      legend.title = element_text(size = 16)
    )

  ggsave(output_file, width = 10, height = 12, dpi = 300)
}

latex_table <- function(df, align, caption, label, digits_map = list(), pvalue_columns = character()) {
  column_names <- names(df)
  header <- paste(escape_latex(column_names), collapse = " & ")

  format_cell <- function(value, column_name) {
    if (column_name %in% pvalue_columns) {
      return(format_p_value(as.numeric(value)))
    }

    if (is.numeric(value)) {
      digits <- digits_map[[column_name]]
      if (is.null(digits)) {
        digits <- 3
      }
      return(format_number(value, digits = digits))
    }

    escape_latex(value)
  }

  body <- lapply(seq_len(nrow(df)), function(row_index) {
    pieces <- vapply(
      seq_along(column_names),
      function(i) format_cell(df[[column_names[[i]]]][[row_index]], column_names[[i]]),
      character(1)
    )
    paste0(paste(pieces, collapse = " & "), " \\\\")
  })

  c(
    sprintf("\\begin{longtable}{%s}", align),
    sprintf("\\caption{%s}\\label{%s}\\\\", caption, label),
    "\\toprule",
    paste0(header, " \\\\"),
    "\\midrule",
    "\\endfirsthead",
    "\\toprule",
    paste0(header, " \\\\"),
    "\\midrule",
    "\\endhead",
    unlist(body, use.names = FALSE),
    "\\bottomrule",
    "\\end{longtable}"
  )
}

build_latex_report <- function(
  output_file,
  workbook_path,
  model_formula,
  total_rows,
  analysis_rows,
  missing_rows,
  type3_table,
  emm_table,
  contrast_table,
  emm_plot_file,
  contrast_plot_file
) {
  type3_latex <- latex_table(
    type3_table,
    align = "lrrrrrr",
    caption = "Type III tests of fixed effects from the mixed-effects model.",
    label = "tab:type3",
    digits_map = list(NumDF = 0, DenDF = 2, `F value` = 3),
    pvalue_columns = "Pr(>F)"
  )

  emm_latex <- latex_table(
    emm_table %>% select(Category, State, emmean, SE, df, lower.CL, upper.CL),
    align = "p{0.33\\linewidth}lrrrrr",
    caption = "Estimated marginal means by state within category.",
    label = "tab:emmeans",
    digits_map = list(emmean = 3, SE = 3, df = 2, lower.CL = 3, upper.CL = 3)
  )

  contrast_latex <- latex_table(
    contrast_table %>% select(Category, contrast, estimate, SE, df, lower.CL, upper.CL, p.value),
    align = "p{0.30\\linewidth}lrrrrrr",
    caption = "Planned contrasts comparing Tennessee with American Samoa and California within each category.",
    label = "tab:contrasts",
    digits_map = list(estimate = 3, SE = 3, df = 2, lower.CL = 3, upper.CL = 3),
    pvalue_columns = "p.value"
  )

  lines <- c(
    "\\documentclass[11pt]{article}",
    "\\usepackage[margin=1in]{geometry}",
    "\\usepackage{booktabs}",
    "\\usepackage{longtable}",
    "\\usepackage{array}",
    "\\usepackage{graphicx}",
    "\\usepackage{float}",
    "\\usepackage{setspace}",
    "\\usepackage[hidelinks]{hyperref}",
    "\\setlength{\\parindent}{0pt}",
    "\\begin{document}",
    "\\title{Mixed-Effects Analysis of Adjusted Cybercrime Rates}",
    "\\author{Automated analysis script}",
    "\\date{\\today}",
    "\\maketitle",
    "\\section{Source data and reshaping}",
    sprintf(
      "The source workbook was \\texttt{%s}. The script extracted the seven annual observations (2016--2022) from the Chattanooga-adjusted summary sheets for American Samoa, Tennessee, and California, then reshaped the eleven cybercrime categories into long format.",
      escape_latex(basename(workbook_path))
    ),
    sprintf(
      "The long-format dataset contains %d state-year-category rows. %d workbook error cell%s %s read as missing, so %d complete observations were used in the mixed-effects model.",
      total_rows,
      nrow(missing_rows),
      ifelse(nrow(missing_rows) == 1, "", "s"),
      ifelse(nrow(missing_rows) == 1, "was", "were"),
      analysis_rows
    ),
    if (nrow(missing_rows) > 0) {
      missing_descriptions <- apply(missing_rows, 1, function(row) {
        sprintf(
          "State %s, Year %s, Category %s",
          row[["State"]],
          row[["Year"]],
          escape_latex(as.character(row[["Category"]]))
        )
      })
      sprintf(
        "The excluded row%s %s.",
        ifelse(length(missing_descriptions) == 1, " was", "s were"),
        paste(missing_descriptions, collapse = "; ")
      )
    } else {
      "No observations were excluded from the model."
    },
    "\\section{Model specification}",
    "The fitted model used State and Category as fixed effects, included their interaction so that within-category contrasts could be estimated directly, and modeled Year as a random intercept:",
    "\\[",
    sprintf(
      "\\mathrm{AdjustedRate}_{ijk} = %s + b_{\\mathrm{Year}_k} + \\varepsilon_{ijk}",
    model_formula
    ),
    "\\]",
    "\\section{Type III tests of fixed effects}",
    type3_latex,
    "\\section{Estimated marginal means}",
    emm_latex,
    "\\section{Planned contrasts}",
    "The planned contrasts were Tennessee versus American Samoa and Tennessee versus California within each category, with no multiplicity adjustment because the comparisons were prespecified.",
    contrast_latex,
    "\\section{Confidence-interval plots}",
    "\\begin{figure}[H]",
    "\\centering",
    sprintf("\\includegraphics[width=\\textwidth]{%s}", basename(emm_plot_file)),
    "\\caption{Estimated marginal means and 95\\% confidence intervals.}",
    "\\end{figure}",
    "\\begin{figure}[H]",
    "\\centering",
    sprintf("\\includegraphics[width=\\textwidth]{%s}", basename(contrast_plot_file)),
    "\\caption{Planned contrast estimates and 95\\% confidence intervals.}",
    "\\end{figure}",
    "\\end{document}"
  )

  writeLines(lines, output_file)
}

main <- function() {
  script_dir <- get_script_dir()
  workbook_path <- normalizePath(file.path(script_dir, "..", workbook_name), mustWork = TRUE)

  old_options <- options(contrasts = c("contr.sum", "contr.poly"))
  on.exit(options(old_options), add = TRUE)

  wide_data <- bind_rows(
    read_adjusted_rate_sheet(workbook_path, sheet_map[["AS"]], "AS"),
    read_adjusted_rate_sheet(workbook_path, sheet_map[["TN"]], "TN"),
    read_adjusted_rate_sheet(workbook_path, sheet_map[["CA"]], "CA")
  )

  long_data <- build_long_data(wide_data)
  missing_rows <- long_data %>% filter(is.na(AdjustedRate))
  analysis_data <- long_data %>% filter(!is.na(AdjustedRate))

  model <- lmer(AdjustedRate ~ State * Category + (1 | Year), data = analysis_data, REML = TRUE)

  type3_table <- anova(model, type = 3) %>%
    to_clean_dataframe(row_name_column = "Effect")

  emm_table <- summary(
    emmeans(model, ~ State | Category, lmer.df = "kenward-roger"),
    infer = c(TRUE, TRUE)
  ) %>%
    to_clean_dataframe()

  contrast_table <- summary(
    contrast(
      emmeans(model, ~ State | Category, lmer.df = "kenward-roger"),
      method = list("TN vs AS" = c(-1, 1, 0), "TN vs CA" = c(0, 1, -1)),
      adjust = "none"
    ),
    infer = c(TRUE, TRUE)
  ) %>%
    to_clean_dataframe() %>%
    mutate(contrast = as.character(contrast))

  emm_plot_file <- file.path(script_dir, "cybercrime_emmeans_ci.png")
  contrast_plot_file <- file.path(script_dir, "cybercrime_contrasts_ci.png")
  make_emm_plot(emm_table, emm_plot_file)
  make_contrast_plot(contrast_table, contrast_plot_file)

  model_summary_file <- file.path(script_dir, "cybercrime_model_summary.txt")
  writeLines(capture.output(summary(model)), model_summary_file)

  write.csv(wide_data, file.path(script_dir, "cybercrime_adjusted_rate_wide.csv"), row.names = FALSE)
  write.csv(long_data, file.path(script_dir, "cybercrime_adjusted_rate_long.csv"), row.names = FALSE)
  write.csv(type3_table, file.path(script_dir, "cybercrime_type3_tests.csv"), row.names = FALSE)
  write.csv(emm_table, file.path(script_dir, "cybercrime_emmeans.csv"), row.names = FALSE)
  write.csv(contrast_table, file.path(script_dir, "cybercrime_planned_contrasts.csv"), row.names = FALSE)

  report_file <- file.path(script_dir, "cybercrime_mixed_effects_report.tex")
  build_latex_report(
    output_file = report_file,
    workbook_path = workbook_path,
    model_formula = "\\beta_0 + \\beta_{\\mathrm{State}_i} + \\beta_{\\mathrm{Category}_j} + \\beta_{\\mathrm{State}\\times\\mathrm{Category}_{ij}}",
    total_rows = nrow(long_data),
    analysis_rows = nrow(analysis_data),
    missing_rows = missing_rows,
    type3_table = type3_table,
    emm_table = emm_table,
    contrast_table = contrast_table,
    emm_plot_file = emm_plot_file,
    contrast_plot_file = contrast_plot_file
  )

  workbook_copy <- createWorkbook()
  addWorksheet(workbook_copy, "Raw_AS")
  addWorksheet(workbook_copy, "Raw_TN")
  addWorksheet(workbook_copy, "Raw_CA")
  addWorksheet(workbook_copy, "Long_Data")
  addWorksheet(workbook_copy, "Analysis_Data")
  addWorksheet(workbook_copy, "TypeIII_Tests")
  addWorksheet(workbook_copy, "EMMeans")
  addWorksheet(workbook_copy, "Planned_Contrasts")

  writeData(workbook_copy, "Raw_AS", wide_data %>% filter(State == "AS"))
  writeData(workbook_copy, "Raw_TN", wide_data %>% filter(State == "TN"))
  writeData(workbook_copy, "Raw_CA", wide_data %>% filter(State == "CA"))
  writeData(workbook_copy, "Long_Data", long_data)
  writeData(workbook_copy, "Analysis_Data", analysis_data)
  writeData(workbook_copy, "TypeIII_Tests", type3_table)
  writeData(workbook_copy, "EMMeans", emm_table)
  writeData(workbook_copy, "Planned_Contrasts", contrast_table)

  output_xlsx <- file.path(script_dir, "cybercrime_mixed_effects_data_copy.xlsx")
  saveWorkbook(workbook_copy, output_xlsx, overwrite = TRUE)

  message("Created analysis outputs in: ", script_dir)
  invisible(NULL)
}

main()
