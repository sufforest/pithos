package main

import (
	"fmt"
	
	"pithos/gen/go/pithos/common"
	"pithos/libs/go/timeutils"
	
	"google.golang.org/protobuf/proto"
)

func main() {
	// 1. Use Shared Library
	currentTime := timeutils.GetCurrentTime()
	fmt.Printf("[%s] Starting Go Proto Demo...\n", currentTime)

	// 2. Use Generated Protobuf
	user := &common.User{
		Name: "Gopher",
		Id:   101,
	}

	fmt.Printf("Created User: %s (ID: %d)\n", user.Name, user.Id)

	// Serialize
	data, err := proto.Marshal(user)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Serialized Size: %d bytes\n", len(data))
	
	// Deserialize
	newUser := &common.User{}
	if err := proto.Unmarshal(data, newUser); err != nil {
		panic(err)
	}
	fmt.Println("Deserialization Success!")
}
