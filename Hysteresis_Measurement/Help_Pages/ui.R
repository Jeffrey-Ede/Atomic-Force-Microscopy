#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#


# Define UI for application that draws a histogram
fluidPage(
  
  navbarPage("Help pages:",
    tabPanel("About",
             includeHTML("About.html")
    ),
    tabPanel("Features",
             includeHTML("Features.html")
    ),
    tabPanel("Controls",
             includeHTML("Controls.html")
    ),
    tabPanel("Voltage Trains",
             includeHTML("voltage_trains_intro.html")
    )
  )
)