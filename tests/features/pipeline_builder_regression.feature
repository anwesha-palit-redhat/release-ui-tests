Feature: Pipeline Builder Regression Tests

  Background:
    Given the user is logged into openshift console
    When the user expands Pipelines in left navigation bar
    And the user navigates to the Pipelines page
    And user switches to current project

  @regression
  Scenario: Create pipeline with tkn and kn tasks, params, yaml edit, workspace, then start
    When the user clicks Create button on Pipelines page
    And the user clicks Pipeline menu item
    Then the user should be on Pipeline Builder page
    When the user fills pipeline name "builder-regression-pipeline" in builder view
    And the user adds task "tkn" in builder view
    And the user adds task "kn" after task "tkn" in builder view
    And the user adds pipeline parameter with name "message" description "greeting" and default "hello"
    And the user switches to YAML view
    And the user updates parameter "message" default to "hello-from-yaml" in YAML view
    And the user switches to Form view
    And the user adds pipeline parameter with name "optional-message" description "optional greeting" and default "optional-hello"
    And the user toggles show required task params only
    And the user toggles show all task params
    And the user adds pipeline workspace with name "source"
    And the user toggles workspace optional view
    And the user toggles workspace required view
    And the user maps task "tkn" workspace "name" to pipeline workspace "source"
    And the user clicks Create button on Pipeline Builder page
    Then the user should be on pipeline details page
    And the pipeline details page should display the pipeline name as "builder-regression-pipeline"
    When the user starts the pipeline
    And the user selects Empty Directory for workspace "source" in Start Pipeline modal
    And the user confirms Start Pipeline
    Then the user should be redirected to a PipelineRun details page
