#include "gtest/gtest.h"
#include "BufferProtocol.h"
#include <iostream>
#include <bitset>
#include <string>
#include <queue>

using namespace std;

queue <char> read_buffer;
queue <char> write_buffer;

void init_serial_protocol() {
    read_buffer = {};
    write_buffer = {};
}

void write_to_read_buffer(const string& str) {
    for (auto &&x : str) read_buffer.push(x);
}

string read_from_write_buffer() {
    string x;
    while (!write_buffer.empty()) {
        x.push_back(write_buffer.front());
        // cout << bitset<8>(write_buffer.front()) << endl;
        write_buffer.pop();
    }
    return x;
}

char SerialProtocol::read() {
    unsigned char ch = read_buffer.front();
    read_buffer.pop();
    return ch;
}

bool SerialProtocol::available() {
    return !read_buffer.empty();
}

void SerialProtocol::write(char ch) {
    write_buffer.push(ch);
}

class BufferProtocolTest : public ::testing::Test {
protected:
    BufferProtocolTest() : bp(&sp) {}
    void SetUp() override {
        init_serial_protocol();
    }
    SerialProtocol sp;
    BufferProtocol bp;
};

TEST_F(BufferProtocolTest, ConstructAndDestruct) {
    BufferProtocol bp(&sp);
}

TEST_F(BufferProtocolTest, ReadWriteOneByte) {
    bp.begin();
    bp.write(0xff);
    bp.end();
    write_to_read_buffer(read_from_write_buffer());
    EXPECT_EQ(bp.read(), BUFFER_T_BEGIN);
    EXPECT_EQ(bp.read(), 0xff);
    EXPECT_EQ(bp.read(), BUFFER_T_END);
}

TEST_F(BufferProtocolTest, ReadWriteBytes) {
    for (int i = 0; i < 32; i++) {
        bp.begin();
        for (int j = 0; j <= i; j++) bp.write(j * 5);
        bp.end();
    }
    write_to_read_buffer(read_from_write_buffer());
    for (int i = 0; i < 32; i++) {
        ASSERT_EQ(bp.read(), BUFFER_T_BEGIN);
        for (int j = 0; j <= i; j++) ASSERT_EQ(bp.read(), j * 5);
        ASSERT_EQ(bp.read(), BUFFER_T_END);
    }
}

TEST_F(BufferProtocolTest, ReadWriteCorruptBytes) {
    for (int i = 0; i < 26; i++) {
        bp.begin();
        for (int j = 0; j < 5; j++) bp.write(i + 'a');
        bp.end();
    }
    auto buffer = read_from_write_buffer();
    while (buffer.length() > 0) {
        write_to_read_buffer(buffer);
        vector <char> bytes;
        while (true) {
            int ch = bp.read();
            if (ch == BUFFER_END) break;
            if (ch == BUFFER_T_END || ch == BUFFER_T_BEGIN) continue;
            bytes.push_back(ch);
        }
        ASSERT_EQ(bytes.size() % 5, 0);
        for (int j = 0; j < bytes.size(); j += 5) {
            for (int k = 1; k < 5; k++) {
                ASSERT_EQ(bytes[j + k], bytes[j]);
            }
        }
        buffer = buffer.substr(1, buffer.size() - 1);
    }
}

TEST_F(BufferProtocolTest, ShouldEndTransaction) {
    ASSERT_EQ(bp.read(), BUFFER_END);
    bp.begin();
    bp.end();
    bp.begin();
    bp.end();
    bp.begin();
    bp.end();
    write_to_read_buffer(read_from_write_buffer());
    ASSERT_EQ(bp.read(), BUFFER_T_BEGIN);
    ASSERT_EQ(bp.read(), BUFFER_T_END);
    ASSERT_EQ(bp.read(), BUFFER_T_BEGIN);
    ASSERT_EQ(bp.read(), BUFFER_T_END);
    ASSERT_EQ(bp.read(), BUFFER_T_BEGIN);
    ASSERT_EQ(bp.read(), BUFFER_T_END);
    ASSERT_EQ(bp.read(), BUFFER_END);
}

TEST_F(BufferProtocolTest, TestAllBytes) {
    bp.begin();
    for (int i = 0; i < 256; i++) bp.write(i);
    bp.end();
    write_to_read_buffer(read_from_write_buffer());
    ASSERT_EQ(bp.read(), BUFFER_T_BEGIN);
    for (int i = 0; i < 256; i++) {
        ASSERT_EQ(bp.read(), i);
    }
    ASSERT_EQ(bp.read(), BUFFER_T_END);
    ASSERT_EQ(bp.read(), BUFFER_END);
}
