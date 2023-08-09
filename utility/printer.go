package utility

import (
	"fmt"
	"github.com/fatih/color"
)

func ClearConsole() {
	fmt.Printf("\x1b[2J")
}

func CriticalMessage(msg ...interface{}) {

	color.Red(fmt.Sprintln(msg...))
}

func CriticalMessageString(msg ...interface{}) string {
	return color.RedString(fmt.Sprintln(msg...))
}

func WarnMessage(msg ...interface{}) {
	color.Yellow(fmt.Sprintln(msg...))
}

func WarnMessageString(msg ...interface{}) string {
	return color.YellowString(fmt.Sprintln(msg...))
}

func InfoMessage(msg ...interface{}) {
	color.Green(fmt.Sprintln(msg...))
}

func InfoMessageString(msg ...interface{}) string {
	return color.GreenString(fmt.Sprintln(msg...))
}

func SpecialMessage(msg ...interface{}) {
	color.Magenta(fmt.Sprintln(msg...))
}

func SpecialMessageString(msg ...interface{}) string {
	return color.MagentaString(fmt.Sprintln(msg...))
}
