#include <stdio.h>
#include <time.h>
#include <stdlib.h>

#define TODAY 13
#define LAST_DAY 31
#define TRAINS_PER_DAY 6
const char* destinations[] = { "Tel Aviv", "Jerusalem", "Haifa", "Eilat", "Be'er Sheva", "Netanya" };
const char* cars[] = {
        "103457",
        "123457",
        "145568",
        "204568",
        "234569",
        "305679",
        "305677",
        "345677",
        "406788",
        "456788",
        "534677",
        "556766",
        "689098",
        "234557",
        "305668",
        "345668",
        "406779",
        "456779",
        "534668",
        "556757",
        "689088"
};

int main() {
    int tabs = 0;
    FILE* in_file = fopen("schedule.txt", "w");
    FILE* in_file1 = fopen("schedule_dates.txt", "w");
    if (!in_file) {
        perror("Failed to open file");
        return 1;
    }
    if (!in_file1) {
        perror("Failed to open file");
        return 1;
    }
    fprintf(in_file, "\"cars\": \n");
    fprintf(in_file, "{\n");
    tabs++; 
    for (int i = 0; i < sizeof(cars)/sizeof(cars[0]); i++) {
        for (int j = 0; j < tabs; j++) fprintf(in_file, "\t");
        fprintf(in_file, "\"%s\":\n", cars[i]);
        for (int j = 0; j < tabs; j++) fprintf(in_file, "\t");
        fprintf(in_file, "{\n");
        tabs++;
        for (int j = 0; j < tabs; j++) fprintf(in_file, "\t");
        fprintf(in_file, "\"seats\":\n");
        for (int j = 0; j < tabs; j++) fprintf(in_file, "\t");
        fprintf(in_file, "{\n");
        tabs++;
        for (int seat = 1; seat <= 32; seat++) {
            for (int j = 0; j < tabs; j++) fprintf(in_file, "\t");
            fprintf(in_file, "\"%d\": {\"Occupied\": %s}", seat, (rand() % 2) ? "true" : "false");
            if (seat < 32) fprintf(in_file, ", \n");
            else fprintf(in_file, "\n");
        }
        tabs--;
        for (int j = 0; j < tabs; j++) fprintf(in_file, "\t");
        fprintf(in_file, "}\n");
        tabs--;
        if (i == (sizeof(cars)/sizeof(cars[0]) - 1)) {
            for (int j = 0; j < tabs; j++) fprintf(in_file, "\t");
            fprintf(in_file, "}\n");
        }
        else {
            for (int j = 0; j < tabs; j++) fprintf(in_file, "\t");
            fprintf(in_file, "},\n");
        }
    }
    tabs--;
    fprintf(in_file, "},\n");
    fprintf(in_file, "\"schedule\": \n");
    tabs++;
    fprintf(in_file, "{\n");
    for (int day = TODAY; day <= LAST_DAY; day++) {
        for (int i = 0; i < tabs; i++) fprintf(in_file, "\t");
        fprintf(in_file, "\"2025-10-%02d\": \n", day);
        fprintf(in_file1, "\"2025-10-%02d\": \n", day);
        for (int i = 0; i < tabs; i++) fprintf(in_file, "\t");
        fprintf(in_file, "{\n");
        tabs++;
        for (int train = 1; train <= TRAINS_PER_DAY; train++) {
            struct tm t = {0};
            t.tm_year = 2025 - 1900; // Year since 1900
            t.tm_mon = 9; // October (0-based)
            t.tm_mday = day;
            t.tm_hour = rand() % 24;
            t.tm_min = rand() % 60;
            t.tm_sec = 0;
            time_t departure_time = mktime(&t);
            for (int i = 0; i < tabs; i++) fprintf(in_file, "\t");
            fprintf(in_file1, "%d:%d \n" , t.tm_hour, t.tm_min);
            fprintf(in_file, "\"%ld\": ", departure_time*1000);
            fprintf(in_file, "{");
            int tr = rand() % 6;
            fprintf(in_file, "\"train\": \"%d\" ,", tr + 1);
            fprintf(in_file, "\"destination\": \"%s\" ,", destinations[tr]);
            fprintf(in_file, "\"platform\": \"%d\" ", (rand() % 2 +1));
            if (train == TRAINS_PER_DAY)
            {
                fprintf(in_file, "}\n");
            }
            else {
                fprintf(in_file, "},\n");
            }
            
        }
        for (int i = 0; i < tabs; i++) fprintf(in_file, "\t");
        if (day == LAST_DAY) {
            fprintf(in_file, "}\n");
        }
        else {
            fprintf(in_file, "},\n");
        }
        tabs--;
    }
    fprintf(in_file, "}\n");
    fclose(in_file);
    fclose(in_file1);
    return 0;
}