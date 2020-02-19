# -*- encoding: utf-8 -*-
import re


class tf2it():
    def convertNumber(self, numbers):
        # number = int(numbers)
        mask = "{0:.2f}"
        snumber = mask.format(numbers)
        split = snumber.split('.')
        postFix = ""
        dnum = int(split[1])
        if dnum > 0:
            if len(split[1]) == 1:
                postFix = " من العشرة"
            else:
                postFix = " من المائة"

        if dnum > 0:
            postFix = " فاصل " + self.convertLong(dnum) + postFix

        result = self.convertLong(int(split[0])) + postFix

        # remove extra spaces!
        result = re.sub(r"^\\s+", "", result)
        result = re.sub(r"\\b\\s{2,}\\b", " ", result)
        return result.strip()

    def convertLong(self, number):
        # 0 to 999 999 999 999
        if number == 0:
            return "صفر"

        snumber = str(number)

        # pad with "0"
        snumber = snumber.zfill(12)

        # XXXnnnnnnnnn
        billions = int(snumber[0:3])
        # nnnXXXnnnnnn
        millions = int(snumber[3:6])
        # nnnnnnXXXnnn
        hundredThousands = int(snumber[6:9])
        # nnnnnnnnnXXX
        thousands = int(snumber[9:12])

        tradBillions = ""
        if billions == 0:
            tradBillions = ""
        elif billions == 1:
            tradBillions = " مليار "
        elif billions == 2:
            tradBillions = " ملياران "
        elif billions >= 3 and billions <= 10:
            tradBillions = self.convertLessThanOneThousand(billions) + " مليارات "
        else:
            tradBillions = self.convertLessThanOneThousand(billions) + " مليار "

        result = tradBillions

        tradMillions = ""
        if millions == 0:
            tradMillions = ""
        elif millions == 1:
            tradMillions = " مليون "
        elif millions == 2:
            tradMillions = " مليونان "
        elif millions >= 3 and millions <= 10:
            tradMillions = self.convertLessThanOneThousand(millions) + " ملايين "
        else:
            tradMillions = self.convertLessThanOneThousand(millions) + " مليون "

        if result.strip() and tradMillions.strip():
            result = result + " و "

        result = result + tradMillions

        tradHundredThousands = ""

        if hundredThousands == 0:
            tradHundredThousands = ""
        elif hundredThousands == 1:
            tradHundredThousands = "ألف "
        elif hundredThousands == 2:
            tradHundredThousands = "ألفان "
        elif hundredThousands >= 3 and hundredThousands <= 10:
            tradHundredThousands = self.convertLessThanOneThousand(hundredThousands) + " آلاف "
        else:
            tradHundredThousands = self.convertLessThanOneThousand(hundredThousands) + " ألف "

        if result.strip() and tradHundredThousands.strip():
            result = result + " و "
        result = result + tradHundredThousands

        tradThousand = self.convertLessThanOneThousand(thousands)
        if result.strip() and tradThousand.strip():
            result = result + " و "
        result = result + tradThousand

        # remove extra spaces!
        result = re.sub(r"^\\s+", "", result)
        result = re.sub(r"\\b\\s{2,}\\b", " ", result)
        return result.strip()

    def convertLessThanOneThousand(self, number):
        soFar = ""

        numNames = [
            "",
            " واحد",
            " اثنان",
            " ثلاثة",
            " اربعة",
            " خمسة",
            " ستة",
            " سبعة",
            " ثمانية",
            " تسعة",
            " عشرة",
            " إحدى عشر",
            " إثنى عشر",
            " ثلاثة عشر",
            " اربعة عشر",
            " خمسة عشر",
            " ستة عشر",
            " سبعة عشر",
            " ثمانية عشر",
            " تسعة عشر"
        ]

        tensNames = [
            "",
            " عشرة",
            " عشرون",
            " ثلاثون",
            " اربعون",
            " خمسون",
            " ستون",
            " سبعون",
            " ثمانون",
            " تسعون"
        ]
        if number % 100 < 20:
            soFar = numNames[number % 100]
            number /= 100;

        else:
            soFar = numNames[number % 10]
            number /= 10;
            if soFar.strip() and tensNames[int(number % 10)].strip():
                soFar = soFar + " و ";
            soFar = soFar + tensNames[int(number % 10)]
            number /= 10;


        result = ""
        if soFar.strip():
            result = " و " + soFar
        else:
            result = soFar

        numberint = int(number)
        if numberint < 0:
            numberint = 0
        if numberint == 0:
            return soFar
        elif numberint == 1:
            return "مائة" + result
        elif numberint == 2:
            return "مائتان" + result
        elif numberint == 8:
            return numNames[numberint][:-2] + "مائة" + result
        else:
            return numNames[numberint][:-1] + "مائة" + result