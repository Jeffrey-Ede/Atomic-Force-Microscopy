#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#

library(shiny)

# Define UI for application that draws a histogram
shinyUI(fluidPage(
  
  navlistPanel(
    "Contents",
    tabPanel("About",
             includeMarkdown("About.md")
    ),
    tabPanel("Features",
             includeMarkdown("Features.md")
    ),
    tabPanel("Controls",
             includeMarkdown("Controls.md")
    )# ),
    # tabPanel("Voltage Trains",
    #          includeMarkdown("voltage_trains_intro.md")
    # )
  )
))
