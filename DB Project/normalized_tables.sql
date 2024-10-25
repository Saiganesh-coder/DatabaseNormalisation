CREATE TABLE `StudentInfo_Hobbies_StudentID_CourseID` (
    `StudentID` VARCHAR(255),
    `CourseID` VARCHAR(255),
    PRIMARY KEY (`StudentID`)
);
CREATE TABLE `StudentInfo_Hobbies_StudentID_Hobbies` (
    `StudentID` VARCHAR(255),
    `Hobbies` VARCHAR(255),
    PRIMARY KEY (`StudentID`)
);
CREATE TABLE `StudentInfo_StudentName_StudentID_StudentName` (
    `StudentID` VARCHAR(255),
    `StudentName` VARCHAR(255),
    PRIMARY KEY (`StudentID`)
);
CREATE TABLE `StudentInfo_CourseName_InstructorID_CourseID_CourseName` (
    `CourseID` VARCHAR(255),
    `CourseName` VARCHAR(255),
    PRIMARY KEY (`CourseID`)
);
CREATE TABLE `StudentInfo_CourseName_InstructorID_CourseID_InstructorID` (
    `CourseID` VARCHAR(255),
    `InstructorID` VARCHAR(255),
    PRIMARY KEY (`CourseID`)
);
CREATE TABLE `StudentInfo_InstructorName_InstructorID_InstructorName` (
    `InstructorID` VARCHAR(255),
    `InstructorName` VARCHAR(255),
    PRIMARY KEY (`InstructorID`)
);
CREATE TABLE `StudentInfo_Semester_CourseID_StudentID_Grade` (
    `Semester` VARCHAR(255),
    `CourseID` VARCHAR(255),
    `StudentID` VARCHAR(255),
    `Grade` VARCHAR(255),
    PRIMARY KEY (`Semester`, `CourseID`, `StudentID`)
);
